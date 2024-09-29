import re
# Define your prompting structure here:

# Functions are used to check if the process should terminate by checking the previous output
# Can also be used to amend the output

def always_true(text):
    return text
def is_yes(text):
    text = re.sub(r'[^a-zA-Z]', '', text)
    text = text.strip().lower()
    if text == "yes":
        return text
    return None

# a preCheck determines if the prompt should be run at all
# This is useful for prompts that are only relevant if a certain condition is met
# In this case, the prompt will skip the stage if it is already a number

def num_check(text):
    text = text.replace(",", "").replace(" ", "")
    return text.isnumeric()

# Check functions can also be used to amend the output
def make_numeric(text):
    text = text.replace(",", "").replace(" ", "")
    return text

# Some usefyl prompts, to save repeating the same text
default_system_prompt = "You are a helpful assistant, asked to examine the content of publications.  You should be conservative with your choices and only provide answers for which there is good evidence in the text. Strictly follow the output formats and never add any other commentary, discussion or conclusions.  "

yes_or_no= "Is this text an affirmative answer?. Answer is a single word, yes or no, and no other commentary. The text is: [reply]"

# The name is used for debug purposes
# The list of prompts are called in sequence - the notation [reply] always refers to the previous output
# [paper] is a special variable that is always available, and refers to the original paper text
# Other variables can be Set by 'putVariable', then referred to in later prompts
# The 'check' function is used to determine if the prompt should exit early
# The 'dataOut' variable is used to store the output of the prompt in the final data structure csv
# The 'hide' variable is just used to hide the I/O from the debug output, so there isn't too much text

summarise = {"name":"Summary",
           "system":default_system_prompt,
           "prompts":
               ["Rewrite the following paper in fewer words.  Make sure to keep all of the technical details, such as mathods, hardware, and software used.  Any species names and protein study information are also really important to keep intact. The paper is [paper]" ],
           "check": always_true,
           "putVariable": "summary",
            "hide": True
           }

is_human = {"name":"Human",
           "system":default_system_prompt,
           "prompts":
               ["Is the following paper a study about humans? This includes human tissue or human diseases.  Answer yes or no. The paper is [summary]" ,
                yes_or_no],
           "check": is_yes,
           "dataOut": "isHuman"
           }
is_phospho = {"name":"Phospho",
           "system":default_system_prompt,
           "prompts":
               ["Is the following paper a phosphoproteomics study that generated new phosphoproteomics data?   Answer yes or no. The paper is [summary]" ,
                yes_or_no],
            "dataOut": "isPhospho",
           "check": is_yes}

count_phospho = {"name":"Phospho Count",
           "system":default_system_prompt,
           "prompts":
               ["How many different sites of phosphorylation were identified in the following paper, in data collected from humans? Give the answer as a single number. The paper is [summary]"
                ],
            "putVariable": "phosphoCountFirst",
           "check": always_true}

count_phospho_2 = {"name":"Phospho Count2",
           "system":default_system_prompt,
           "preCheck": num_check,
           "prompts":
               [
                "I wish to verify the number in this generated text.  Express it exactly as a single number: 0 if there are none, of if there is an unknown number, put 99. If it already numeric, do not change the number. The generated text is [phosphoCountFirst]"
                ],
                "dataOut": "PhosphoCount",
           "check": make_numeric}


# prompt_data defines the structure you will use (the order of the prompts)


prompt_data = [summarise, is_human, is_phospho, count_phospho, count_phospho_2]
