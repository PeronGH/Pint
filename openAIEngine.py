import os
from openai import OpenAI
import json
import hashlib
from prompt_data import model_data

model_engine = model_data["model_name"]

class OpenAIEngine:
    def __init__(self, key=None, cache_folder="cache"):

        if key is None:
            key = os.environ.get("OPENAI_API_KEY")

        self.client  = OpenAI(api_key=key)
        self.cache_folder = cache_folder

    def prompt(self, prompt, system=""):

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        response = self.create_chat_completion(messages)
        return response["choices"][0]["message"]["content"]

    # create_chat_completion is used internally for API compatibility
    def create_chat_completion(self, messages):

        # Build a cache key using the model engine, system, and prompt
        hashkey = ".".join(["openai-prompt-caching-v1", model_engine, messages[0]['content'], messages[1]['content']])
        hash_key = hashlib.md5(hashkey.encode()).hexdigest()
        filename = f"{self.cache_folder}/{hash_key}.json"

        # If the response is cached, load it from the cache
        if os.path.exists(filename):
            with open(filename, "r") as file:
                cached_message = json.load(file)
        else:
            response = self.client.chat.completions.create(
                model=model_engine,
                messages=messages,
                max_tokens=4024,
                temperature=0,
                n=1,
            )

            content = response.choices[0].message.content

            cached_message = {"message": {"content": content}}
            with open(filename, "w") as file:
                json.dump(cached_message, file)

        return {"choices": [cached_message]}
