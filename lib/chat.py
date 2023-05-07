import openai
from setting import OFFLINE_CHATGPT, DEFAULT_MODEL

import logging
logger = logging.getLogger(__name__)


class MyBotWrapper:
    def __init__(self, parser, model=DEFAULT_MODEL, temperature=0.5) -> None:
        self.parser = parser
        self.model = model
        self.temperature = temperature
    
    def run(self, inputs):
        prompt = self.parser.compose_prompt(inputs=inputs)
        logger.debug(f"PROMPT: {prompt}")
        if OFFLINE_CHATGPT:
            res = self.parser.get_sample_response(prompt=prompt)
            logger.debug(f"PARSED RESPONSE: {res}")
        else:
            response = self.get_completion(prompt=prompt)
            logger.debug(f"RAW RESPONSE: {response}")
            res = self.parser.parse_response(prompt=prompt, response=response)
            logger.debug(f"PARSED RESPONSE: {res}")
        return res

    def get_completion(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    @property
    def task_name(self):
        return self.parser.task_name if self.parser else ""
