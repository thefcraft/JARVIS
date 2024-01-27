from .constants import *
import openai

openai.api_base = api_base
openai.api_key = api_key

class llm:
    def __init__(self, system_prompt="Below is an instruction that describes a task. Write a response that appropriately completes the request.", num_history_prompts=10):
        self.default = [{"role": "system", "content": system_prompt}]
        self.messages = []
        self.num_history_prompts = num_history_prompts
        
    def __call__(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        if len(self.messages)>self.num_history_prompts: self.messages = self.messages[1:]
        # self.messages.append({"role": "assistant", "content": response})
        completion = openai.ChatCompletion.create(
            model="local-model", # this field is currently unused
            messages=self.default+self.messages, 
            stream = True
        )
        response = ''

        for chunk in completion:
            chunk = chunk.choices[0]['delta'].get("content", "")
            response+=chunk
            yield chunk
        self.messages.append({"role": "assistant", "content": response})