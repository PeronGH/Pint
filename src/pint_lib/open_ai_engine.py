import os

import json
import hashlib
from .model_data import get_model_data

from .prompt_cache_sqlite import PromptCache   




class OpenAIEngine:
    def __init__(self, key=None, cache_folder="cache", max_tokens = 4096):
        try:
            from openai import OpenAI
        except:
            raise RuntimeError("To use ChatGPT, the openai package must be installed.")
            
        
        if key is None:
            key = os.environ.get("OPENAI_API_KEY")
        if key is None:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        model_data = get_model_data()
        self.model_engine = model_data["model_name"]
        self.max_tokens = max_tokens        
        self.client  = OpenAI(api_key=key)
        self.cache_folder = cache_folder
        self.cache = PromptCache(cache_folder)  # Use the imported cache class

    def prompt(self, prompt, system=""):

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        response = self.create_chat_completion(messages)
        return response["choices"][0]["message"]["content"]

    # create_chat_completion is used internally for API compatibility
    def create_chat_completion(self, messages):

 

        cached_response = self.cache.get_cached_response(self.model_engine, system, prompt)
        if cached_response:
            return {"choices": [cached_response]}
            
            
 
        response = self.client.chat.completions.create(
            model=self.model_engine,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0,
            n=1,
        )

        content = response.choices[0].message.content

        cached_message = {"message": {"content": content}}
        self.cache.save_response(self.model_engine, system, prompt, cached_message)

        return {"choices": [cached_message]}
