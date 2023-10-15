import json
from lib.utils import cloze_sentence

import logging
logger = logging.getLogger(__name__)


class ParserBase():
    """Parser is a class that is responsible for generating prompt and 
    parsing the response from ChatGPT.
    
    Returns:
        dict: {"success": bool, "raw_response": str, "result": str, ...}
    """
    failure = ""
    result_key = "result"
    task_name = "<Abstract>"
    
    def __init__(self):
        self.inputs = None
    
    def compose_prompt(self, inputs):
        """Compose the prompt for ChatGPT from inputs

        Args:
            inputs (dict): any inputs that are needed to compose the prompt

        Returns:
            str: prompt for ChatGPT
        """
        self.inputs = inputs
        return ""
    
    def parse_response(self, prompt, response):
        """Parse the response from ChatGPT into desired format

        Args:
            prompt (str): prompt given to ChatGPT
            response (str): raw response from ChatGPT

        Returns:
            dict: parsed response
        """
        success = not self.response_failed(response=response)
        return {
            'success': success,
            'prompt': prompt,
            'raw_response': response,
            self.result_key: response,
            **self.inputs,
        }
                
    def response_failed(self, response):
        error_list = [
            "Failed to read response from ChatGPT",
            "against OpenAI's content policy",
        ]
        for err_msg in error_list:
            if err_msg in response.lower():
                logger.error(response)
                return True
        return False
    
    @staticmethod
    def remove_surrounding_quotes(text:str) -> str:
        """Remove surrounding quotes from a string

        Args:
            text (str): string possibly with surrounding quotes

        Returns:
            str: string without surrounding quotes
        """
        if text.startswith('"'):
            text = text[1:]
        if text.endswith('"'):
            text = text[:-1]
        return text

    def get_sample_response(self, prompt):
        return ""


class ParaphraseParser(ParserBase):
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        original = inputs['original']
        return 'Paraphrase "{original}"'.format(original=original)
    
    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        response = self.remove_surrounding_quotes(response)
            
        return {
            'original': self.inputs['original'],
            'paraphrase': response,
            **res,
        }
    
    def get_sample_response(self, prompt):
        return {
            'original': "I like to eat apples.",
            'paraphrase': "I enjoy eating apples.",
        }


class SemanticParser(ParserBase):
    """Parse the result of semantic clusters from ChatGPT
    """
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        words = inputs['words']
        cluster_size = inputs.get('cluster_size', 6)
        
        return 'Group the following words into {cluster_size} clusters based on their semantic similarity: "{words}"' \
                .format(cluster_size=cluster_size,
                    words=", ".join(words))
    
    def parse_response(self, prompt, response):
        res = super().parse_response(response=response)
        response = self.remove_surrounding_quotes(response)            
        
        return {
            'original': self.inputs['original'],
            'paraphrase': response,
            **res,
        }
    
    def get_sample_response(self, prompt):
        return {
            'original': "I like to eat apples.",
            'paraphrase': "I enjoy eating apples.",
        }


class SentGenParser(ParserBase):
    """Parse the generated sentence from ChatGPT
    
    inputs={"word": "account", "tag": "NN"}
    
    return {"success": True, "result": "I have an ____ with the bank.", "word": "account", "tag": "NN"}
    """
    task_name = "Sentence Generation"
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        word = inputs.get('word')
        tag = inputs.get('tag', 'any')
        domain = inputs.get('domain', 'Academic English')
        max_words = inputs.get('max_words', 20)
        delimiter = self.inputs.get('delimiter', 'a backtick')
        
        jj_requirement = ''
        if tag == 'JJ':
            jj_requirement = f'- Ensure "{word}" be followed by a noun. '
        
        prompt = f'''Create a sentence in the domain of {domain} that meets the following criteria:
- The sentence should contain the word "{word}" tagged as "{tag}".
- The length of the sentence should be between 20 to 30 words.
- Ensure "{word}" is not used at the beginning of the sentence or repeated elsewhere in the sentence.
{jj_requirement}\
- Preferably, do not start the sentence with the word "the".
To give you a clearer idea, consider this example: If the provided word was "account" tagged as "NN" (noun),\
an appropriate sentence would be:
I have an account with the bank.
'''
        return prompt

    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        response = self.remove_surrounding_quotes(response)
        
        word = self.inputs.get('word')
        
        if word not in response:
            logger.error(f"Keyword '{word}' not found in response: {response}")
            return {
                **res,
                "success": False,
            }
        
        if response.startswith(word):
            logger.error(f"Keyword '{word}' found at the beginning of the sentence: {response}")
            return {
                **res,
                "success": False,
            }
        
        result = cloze_sentence(response, word)
        
        return {
            **res,
            "result": result,
        }
    
    def get_sample_response(self, prompt):
        return {
            "success": True, 
            "result": "I have an ____ with the bank.", 
            "word": "account", 
            "tag": "NN",
        }


class PosCheckParser(ParserBase):
    """Check whether a word has a given pos tag in a sentence

    inputs = {"word": "account", "tag": "NN", "sentence": "I have an account with the bank."}
    
    return {"success": True, "word": "account", "tag": "NN", "sentence": "I have an account with the bank."}
    """
    task_name = "POS Check"
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        word = inputs.get('word')
        sentence = inputs.get('sentence')
        
        prompt = f'''What is the POS tag of the word "{word}" \
in the following sentence. Reply with the POS tag only.
---
{sentence}
'''
        return prompt
    
    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        result = self.inputs.get('tag').lower() == response.lower()
        return {
            **res,
            "success": result,
        }


class DerivativeParser(ParserBase):
    """Parse the derivatives of a word
    
    inputs={"word": "account"}
    
    return {"success": True, "response": "accounts, accounting, accounted, accountant, accountancy", "word": "account" }
    """
    task_name = "Derivative Collection"
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        word = inputs.get('word')
        prompt = f"""Give me all derivatives of the word delimited by tripple backticks. \
Delimit the derivatives with a comma. \
```{word}```"""
# List the derivatives in descending order of frequency. \

#         prompt = f"""Give me all one-word derivatives of the following word \
# delimited by tripple backticks. List the derivatives with a comma. \
# ```{word}```"""

        return prompt
    
    def get_sample_response(self, prompt):
        return {
            "success": True,
            "result": "accounts, accounting, accounted, accountant, accountancy", 
            "word": "account" 
        }


class RationalParser(ParserBase):
    """Test the rationality of several words in a sentence
    
    inputs={"words": ["account", "apple"], "sentence": "I have an ______ with the bank."}
    
    return {"success": True, "result": {"account": True, "apple": False}, "good_candidates": ["apple"], "others": ["account"], "words": ["account", "bank"], "sentence": "I have an ______ with the bank."}
    """
    task_name = "Rationality Test"
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        keyword = inputs.get('keyword')
        candidates = inputs.get('candidates')
        words_with_comma = ", ".join(set(str(w) for w in candidates))
        sentence = inputs.get('sentence')
        
        prompt = f'''In this multiple choice cloze question stem: "{sentence}" The key is "{keyword}".\
A list of possible distractors include "{words_with_comma}". Please provide feedback in terms of \
"syntactic appropriateness" and "contextual/semantic appropriateness" of the distractors in the completed sentences. \
Return only the following result in JSON format to me:
{{
  "distractor 1": {{"syntax": true, "semantics": true}},
  "distractor 2": {{"syntax": true, "semantics": false}}
}}

To provide you with an example, the question stem is "Birds _____ in the sky." The key is "fly". \
The list of distractors include "swim, beat". The distractor "swim" is syntactically valid because \
there will be no grammar errors when it is filled into the blank, but it's contextually inappropriate \
since birds "fly" in the sky, not "swim". The distractor "beat" is syntactically invalid because "beat" \
is a transitive verb and requires an object after it. There will be  grammar errors when it is filled into the blank. \
It's contextually/semantically inappropriate because the sentence does not make much sense or is making less sense compared with the key. \
Return only the following result in JSON format to me:
{{
  "swim": {{"syntax": true, "semantics": false}},
  "beat": {{"syntax": false, "semantics": false}}
}}

'''
# Reply with json object only without any notes. 
# while using correct articles and prepositions, \

        return prompt

    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        try:
            obj = json.loads(response)
            others = []
            good_candidates = []
            candidates = self.inputs['candidates']
            for k, v in obj.items():
                candidate = next(filter(lambda w: str(w) == k, candidates), "ERROR")
                if v['syntax'] and not v['semantics']:
                    # the word is a good candidate as a distractor 
                    #   if it is syntactically correct but semantically wrong
                    good_candidates.append(candidate)
                else:
                    others.append(candidate)
            return {
                **res,
                "result": obj,
                "good_candidates": good_candidates,
                "others": others,
            }
        except json.decoder.JSONDecodeError as e:
            return {
                **res,
                "success": False,
            }
        
    
    def get_sample_response(self, prompt):
        return {
            "success": True,
            "others": ["account"],
            "good_candidates": ["bank"],
            "response": {"account": True, "bank": False}, 
            "words": ["account", "bank"], 
            "sentence": "I have an ______ with the bank."
        }



