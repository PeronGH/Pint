
import os
import anthropic
import json

import hashlib
from prompt_data import model_data
model_engine = model_data["model_name"]


class ExternalEngine:
    def __init__(self, cache_folder="cache"):

        self.cache_folder = cache_folder

    def prompt(self, prompt, system = ""):
        messages = [ {"role": "system", "content": system}, {"role": "user", "content": prompt}]
        response = self.create_chat_completion(messages)
        return response["choices"][0]["message"]["content"]

    #This is used for API compatibility
    def create_chat_completion(self, messages):

        prompt=""
        system = ""
        for m in messages:
            if m["role"] == "user":
                prompt += m["content"]
            if m["role"] == "system":
                system += m["content"]

        hashkey = ".".join(["prompt-caching-v1", model_engine, system, prompt])


        hash = hashlib.md5(hashkey.encode()).hexdigest()

        filename = f"{self.cache_folder}/{hash}.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                message = json.load(file)

        else:

            localPrompt = {"prompt": prompt, "system": system}
            # call external.sh and read output from shell

            content = os.popen(f'./external_prompt.sh "{localPrompt}"').read()

            message = {"message": {"content": content}}
            with open(filename, "w") as file:
                json.dump(message, file)



        choices = [message]
        response = {"choices":choices}
        return response

