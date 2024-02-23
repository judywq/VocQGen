import json
import re
from lib.utils import cloze_sentence, replace_article

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
    response_format = 'text' # 'text' | 'json_object'
    
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
        # sense = inputs.get('sense', None)
        country = inputs.get('country', 'Japanese')
        domain = inputs.get('domain', 'General Academic')
        scope = inputs.get('scope', 'a wide range of general topics your students may know that does not require domain-specific English knowledge')
        level_start = inputs.get('level_start', 'A2')
        level_end = inputs.get('level_end', 'lower B2')
        
        # if sense:
        #     sense_part = f'with the meaning of "{sense}"'
        # else:
        #     sense_part = ''
        #  "with the definition: {sense_part}"
        
        prompt = f'''You are an English teacher at a {country} university and you are creating exemplary sentences to show your students \
the use of specific English words in the domain of English for {domain} Purposes.
The English proficiency of your students ranges from {level_start} to {level_end} based on CEFR. They are second language learners in Japan.
Now please create a sentence for the word "{word}" tagged as "{tag}". 
The sentence should meet the following criteria:

The sentence should be contextualized in {scope}.
The sentence should show a frequent N-gram (N<=3) collocation of the word "{word}" tagged as "{tag}" with the specified definition.
The word "{word}" should be pivotal to the meaning of the sentence and carries significant weight in the context. 
The sentence should be understandable to the target students, with no words beyond their proficiency levels.
The length of the sentence should be between 15-20 words.
Ensure "{word}" does not appear at the beginning or the end of the sentence, nor is it repeated elsewhere in the sentence.
Ensure none of the derivatives of "{word}" are present in the sentence.
Please avoid starting the sentence with the definite article "the" as much as possible.
Return the sentence and the collocation in the JSON format as follows:
{{
  "sentence": "generated sentence",
  "collocation": "collocation of the word"
}}

Example: If the provided word is "account", tagged as "NN", with the definition: 
"a record of debit and credit entries to cover transactions involving a particular item or a particular person or concern".
an appropriate response can be:
{{
  "sentence": "In managing finances, maintaining a bank account is essential for every student.",
  "collocation": "bank account"
}}
'''
        return prompt

    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        
        
        response = self.remove_surrounding_quotes(response)
        try:
            obj = json.loads(response)
            sentence = obj.get('sentence', '')
            collocation = obj.get('collocation', '')
            word = self.inputs.get('word')
            pat = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            if not pat.search(sentence):
                logger.warning(f"Keyword '{word}' not found in sentence: {sentence}")
                return {
                    **res,
                    "success": False,
                }

            if sentence.startswith(word):
                logger.warning(f"Keyword '{word}' found at the beginning of the sentence: {sentence}")
                return {
                    **res,
                    "success": False,
                }
            
            # Replace the keyword with a blank
            clozed_sentence = cloze_sentence(sentence, word)
            
            # Replace "a" or "an" with "a/an" before the blank
            clozed_sentence = replace_article(clozed_sentence)
            
            return {
                **res,
                "result": {
                    "sentence": clozed_sentence,
                    "collocation": collocation,
                           },
            }
        except json.decoder.JSONDecodeError as e:
            return {
                **res,
                "success": False,
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
    
    inputs={"candidates": ["account", "apple"], "sentence": "I have an ______ with the bank."}
    
    return {"success": True, "result": {"account": True, "apple": False}, "good_candidates": ["apple"], "others": ["account"], "words": ["account", "bank"], "sentence": "I have an ______ with the bank."}
    """
    task_name = "Rationality Test"
    response_format = 'json_object'
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        keyword = inputs.get('keyword')
        candidates = inputs.get('candidates')
        words_with_comma = ", ".join(set(str(w) for w in candidates))
        sentence = inputs.get('sentence')
        
        prompt = f'''You are a university English teacher and you are creating distractors for vocabulary multiple-choice cloze questions for your students.
In this question stem: "{sentence}"
A list of possible distractors include "{words_with_comma}". 
Please evaluate the syntactic appropriateness/grammatical accuracy and contextual appropriateness/semantic sense-making of the distractors in the completed sentences.
Return only the following result in JSON format:
{{
  "distractor 1": {{"syntax": true, "semantics": true}},
  "distractor 2": {{"syntax": true, "semantics": false}}
}}

Example: In the question stem: "Birds _____ in the sky." the key is "fly". The list of distractors include "swim, pick". The distractor "swim" is syntactically appropriate because there will be no grammar errors when it is filled into the blank, but it does not make sense since birds "fly" in the sky, not "swim". The distractor "pick" is syntactically inappropriate because "pick" is a transitive verb and requires an object after it. There will be  grammar errors when it is filled into the blank. It also does not make much sense. Thus the returned result in JSON format is as follows:
{{
  "swim": {{"syntax": true, "semantics": false}},
  "pick": {{"syntax": false, "semantics": false}}
}}'''
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
                candidate = next(filter(lambda w: str(w) == k, candidates), None)
                if not candidate:
                    logger.warning(f"Cannot find candidate '{k}' in response: {candidates}")
                    continue
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


class PosRankParser(ParserBase):
    """Get the most frequently used pos of a word
    
    inputs={"keyword": "account", tags: ["..."]}
    
    return {"success": True, "result": ["..."]} }
    """
    task_name = "POS Ranking"
    response_format = 'json_object'
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        keyword = inputs.get('keyword')
        student_type = inputs.get('student_type', 'Japanese university ESL students')
        tags = inputs.get('tags', [])
        pos_list = ",".join(tags)
        
        prompt = f'''For the word "{keyword}", the following is a list of Part of Speech it can take on.
Shortlist the POS tags by deciding which POS tags reflect the common usage of the word. 
Then sort the shortlisted POS tags in terms of use frequency in descending order.
Please do not add any new POS tags.
Respond in JSON format in this form: {{"common_pos": [...]}}. 
List of POSs: {pos_list}'''

        return prompt

    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        try:
            obj = json.loads(response)
            top_pos = obj.get('common_pos', [])
            return {
                **res,
                "result": top_pos,
            }
        except json.decoder.JSONDecodeError as e:
            return {
                **res,
                "success": False,
            }



class SenseRankParser(ParserBase):
    """Get the most frequently used senses of a word
    
    inputs={"keyword": "account", "tag": "VB", senses: ["..."]}
    
    return {"success": True, "result": ["..."]} }
    """
    task_name = "Sense Ranking"
    response_format = 'json_object'
    
    def compose_prompt(self, inputs):
        super().compose_prompt(inputs=inputs)
        keyword = inputs.get('keyword')
        tag = inputs.get('tag')
        student_type = inputs.get('student_type', 'Japanese university ESL students')
        senses = inputs.get('senses', [])
        sense_list = "\n".join(senses)
        
        prompt = f'''For the word "{keyword}" tagged as {tag},  the following is a list of definitions.
Consolidate the similar definitions and shortlist the definitions that are most likely to be familiar to the following students.
Then sort the shortlisted definitions based on student familiarity in descending order.
Please do not add any new definitions to this shortlist, and keep at least 1 definition.
Students: {student_type}
Respond in JSON format in this form: {{"shortlisted_definitions": [...]}}.
List of definitions:
{sense_list}'''

        return prompt

    def parse_response(self, prompt, response):
        res = super().parse_response(prompt=prompt, response=response)
        try:
            obj = json.loads(response)
            top_senses = obj.get('shortlisted_definitions', [])
            return {
                **res,
                "result": top_senses,
            }
        except json.decoder.JSONDecodeError as e:
            return {
                **res,
                "success": False,
            }



