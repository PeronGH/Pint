
import os
import anthropic
import json

import hashlib

model_engine = "claude-3-haiku-20240307"

class ClaudeEngine:
    def __init__(self, key=None, cache_folder="cache"):
        if key == None:
            key = os.environ["ANTHROPIC_API_KEY"]
        self.client = anthropic.Anthropic(
        api_key=key, )
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

        key = ".".join(["prompt-caching-v1", model_engine, system, prompt])


        hash = hashlib.md5(key.encode()).hexdigest()

        filename = f"{self.cache_folder}/{hash}.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                message = json.load(file)

        else:
            message = self.client.messages.create(
            model= model_engine,
            system=system,
            max_tokens=4024,
            messages=[
                {"role": "user", "content": prompt}
            ]   )
            message = {"message": {"content": message.content[0].text}}
            with open(filename, "w") as file:
                json.dump(message, file)



        choices = [message]
        response = {"choices":choices}
        return response

