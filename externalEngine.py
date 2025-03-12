
import os
import anthropic
import json
import subprocess
import base64
import hashlib
from prompt_data import model_data
model_engine = model_data["model_name"]
llm_script = model_data.get("llm_script")

USE_CACHE = True

class ExternalEngine:
    def __init__(self, cache_folder="cache" ):

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
        if USE_CACHE and os.path.exists(filename):
            with open(filename, "r") as file:
                message = json.load(file)

        else:


# Calculate the total size of the environment variables
 

                        
          #  localPrompt = {"prompt": prompt, "system": system}
            # call external.sh and read output from shell

            local_prompt = {"prompt": prompt, "system": system}
            local_prompt = json.dumps(local_prompt)

            # this is not needed - so removed for simplicity of using without needing to decode
     #       encoded_prompt = base64.b64encode(local_prompt.encode()).decode()

            lm_script = '/mnt/hc-storage/users/tony/share/llm_server/promptin.sh'
            result = subprocess.run(
            [llm_script],
            input=local_prompt,  # Pass the data via stdin
            capture_output=True,
            text=True,
            check=True )
            
            #result = subprocess.run([llm_script,local_prompt], capture_output=True, text=True, check=True)
            
            content = result.stdout
            
            
            
            message = {"message": {"content": content}}
            with open(filename, "w") as file:
                json.dump(message, file)



        choices = [message]
        response = {"choices":choices}
        return response

