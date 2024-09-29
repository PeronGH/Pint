import os
from openai import OpenAI
import json
import hashlib

# The model you want to use (GPT-4 in this case)
model_engine = "gpt-4-turbo"

class OpenAIEngine:
    def __init__(self, key=None, cache_folder="cache"):
        # Set the OpenAI API key either from input or from environment variables
        if key is None:
            key = os.environ.get("OPENAI_API_KEY")

        self.client  = OpenAI(api_key=key)
        self.cache_folder = cache_folder

    def prompt(self, prompt, system=""):
        """Send a user prompt to the model with an optional system message."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        response = self.create_chat_completion(messages)
        return response["choices"][0]["message"]["content"]

    def create_chat_completion(self, messages):
        """Handle chat completion creation with caching support."""
        # Build a cache key using the model engine, system, and prompt
        key = ".".join(["prompt-caching-v1", model_engine, messages[0]['content'], messages[1]['content']])
        hash_key = hashlib.md5(key.encode()).hexdigest()
        filename = f"{self.cache_folder}/{hash_key}.json"

        # If the response is cached, load it from the cache
        if os.path.exists(filename):
            with open(filename, "r") as file:
                cached_message = json.load(file)
        else:
            # If not cached, make the API call to OpenAI's new unified completions endpoint
            response = self.client.chat.completions.create(
                model=model_engine,
                messages=messages,
                max_tokens=4024,  # Adjust token limit based on your needs
                temperature=0,  # Optional: Adjust creativity level
                n=1,  # Optional: Number of completions to generate
            )

            # Cache the response for future use
            content = response.choices[0].message.content


            cached_message = {"message": {"content": content}}
            with open(filename, "w") as file:
                json.dump(cached_message, file)

        # Wrap the cached message into a format similar to the API response
        return {"choices": [cached_message]}
