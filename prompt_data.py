import re

#model is openai or claude
#model_name gets passed to the api
#api_key - your api key as text, ("sk-proj...") or if None, it will look for an environment variable - OPENAI_API_KEY or ANTHROPIC_API_KEY
#file_path is the path to a csv containing pubmed ids
#column_name is the name of the column that contains the pubmed if
#sections_to_extract is the sections of the paper to extract - If None it will extract all of the sections.  These sections can be referred to individually in the prompts


model_data = {
    "model": "claude",
    "model_name": "claude-3-haiku-20240307",
    "api_key": None,
    "file" : 'data/Human phosphorylation datasets 2024.csv',
    "column_name" : 'pubmed_id',
    "sections" : ["abstract", "intro", "methods", "results", "discuss","concl" ]

}
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
proteomics_system_prompt = "You are a helpful assistant, asked to examine the content of publications. You should be an expert in proteomics studies, to do with proteins, peptides, post-translational modifications and the equipment settings and software that are used to perform these experiments.  You should be conservative with your choices and only provide answers for which there is good evidence in the text. Strictly follow the output formats and never add any other commentary, discussion or conclusions.  "

basic_system_prompt = "You are a helpful assistant. You will be asked to examine the content of publications for further analysis.  You should be conservative with your choices and only provide answers for which there is good evidence in the text. You may be required to output in specific formats, you must always strictly follow the output formats and never add any other commentary, discussion or conclusions.  "

yes_or_no= "Is this text an affirmative answer? Answer is a single word, yes or no, and no other commentary. The text is: [reply]"

# The name is used for debug purposes
# The list of prompts are called in sequence - the notation [reply] always refers to the previous output
# [paper] is a special variable that is always available, and refers to the original paper text
# Paper Sections can also be referred to by [section_name] e.g., [methods]

# Other variables can be set by 'putVariable', then referred to in later prompts
# The 'check' function is used to determine if the prompt should exit early
# The 'dataOut' variable is used to store the output of the prompt in the final data structure csv
# The 'hide' variable is just used to hide the I/O from the debug output, so there isn't too much text

summarise = {"name":"Summary",
           "system":proteomics_system_prompt,
           "prompts":
               ["Rewrite the following paper in fewer words.  Make sure to keep all of the technical details, such as mathods, hardware, and software used.  Any species names and protein study information are also really important to keep intact. The paper is [paper]" ],
           "check": always_true,
           "putVariable": "summary",
            "hide": True
           }

is_human = {"name":"Human",
           "system":basic_system_prompt,
           "prompts":
               ["Does the following paper involve a study with humans? This includes data from human tissue or diseases in humans (homo sapiens).  Answer yes or no. The paper is [summary]" ,
                yes_or_no],
           "check": is_yes,
           "dataOut": "isHuman"
           }

get_software = {"name":"methods",
           "system":proteomics_system_prompt,
           "prompts":
               ["Is the following methods section, what software was used for a protein search engine was employed?  Popular examples include ProteomeDiscoverer / Mascot, MaxQuant or Fragpipe.  This is not an exhaustive list, other software may be available.  The section to analyze is [methods]", "Convert the following text into a comma-separated list of software names, including version numbers, with no other commentary - this will be used in automated analysis. If no specific software is identified, give an empty list: [reply]" ],
           "check": always_true,
           "dataOut": "software"
           }

is_phospho = {"name":"Phospho",
           "system":proteomics_system_prompt,
           "prompts":
               ["Does the following text discuss a study that generated phosphoproteomics data?  e.g., did they report identifying or quantifying any phosphorylation sites (phosphosites)?  Answer yes or no. The text is [summary]" ,
                yes_or_no],
            "dataOut": "isPhospho",
           "check": is_yes}
is_public = {"name":"IsPublic",
           "system":proteomics_system_prompt,
           "prompts":
               ["Does the following paper claim that they have added or depositied any data for public access?  This includes any public data repository or website, such as ProteomeXchange, Pride, Github, etc.  Answer yes or no. The text is [paper]" ,
                yes_or_no],
            "dataOut": "isPublic",
           "check": always_true}


count_phospho = {"name":"Phospho Count",
           "system":proteomics_system_prompt,
           "prompts":
               ["How many different sites of phosphorylation were claimed to identified in the following study? We are only intested in the number of sites, not the number of proteins as this will be answered later. We are not interested in other post translational modifications at this stage. Give the answer as a single number with no other commentary. The paper is [summary]"
                ],
            "putVariable": "phosphoCountFirst",
           "check": always_true}

count_phospho_check = {"name":"Phospho Count2",
           "system":basic_system_prompt,
           "preCheck": num_check,
           "prompts":
               [
                "I wish to verify the number in this generated text.  Express it exactly as a single number: 0 if there are none, of if there is an unknown number, put 99. If it is already numeric, do not change the number. The generated text is [phosphoCountFirst]"
                ],
                "dataOut": "PhosphoCount",
           "check": make_numeric}

count_phospho_proteins = {"name":"PhosphoProtein Count",
           "system":proteomics_system_prompt,
           "prompts":
               ["how many phosphorylated proteins or phosphoproteins were measured or identified in the following study? We are only intested in the number of proteins, not the number of sites, as this will be answered later. We are not interested in other post translational modifications at this stage. Give the answer as a single number with no other commentary. The paper is [summary]"
                ],
            "putVariable": "phosphoProteinCountFirst",
           "check": always_true}

count_phospho_proteins_check = {"name":"PhosphoProtein Count2",
           "system":basic_system_prompt,
           "preCheck": num_check,
           "prompts":
               [
                "I wish to verify the number in this generated text.  Express it exactly as a single number: 0 if there are none, of if there is an unknown number, put 99. If it is already numeric, do not change the number. The generated text is [phosphoProteinCountFirst]"
                ],
                "dataOut": "PhosphoProteinCount",
           "check": make_numeric}

# prompt_data defines the structure you will use (the order of the prompts)
dia_query = {"name":"DIA query",
           "system":proteomics_system_prompt,
           "prompts":
               [
                "The following text is the methods from a proteomics study.  We need to know if this study employed DDA (Data Dependent Acquisition) mass spectrometry or alternatively employed DIA (Data Independent Acquisition) mass spectrometry. DIA is sometimes also called SWATH or all ion fragmentation (AIF). Some software, such as DIA-NN, Spectronaut, Skyline, or OpenSWATH are commonly used for DIA.    The methods text is: [methods]    ",
                     "Convert the following text, extracted from a proteomics study, into a comma-separated list with no other commentary.  The list should only contain DIA or DDA, depending on what is indicated by the text.  The text is:  [reply]"

                ],
                "dataOut": "DIAQuery",
           "check": always_true}
# prompt_data defines the structure you will use (the order of the prompts)
settings_query = {"name":"tolerance query",
           "system":proteomics_system_prompt,
           "prompts":
               [
                " We need to know any precursor and fragment tolerance settings that were used.  These may be expressed as parts per million (ppm) or Daltons (Da). Give just the answers  with no other commentary.  The methods text is: [methods]    ",
                   "Convert the following text extracted from a proteomics study into a comma-separated list of possible  precursor and fragment tolerance settings, with no other commentary - this will be used in automated analysis. If no specific values are identified, give an empty list. The text is: [reply].  End of text."

               ],
                "dataOut": "Tolerance",
           "check": always_true}

ptm_query = {"name":"ptm query",
           "system": "You are a helpful assistant understanding protemics studies.  Post-translational modifications are changes that happen to a protein, some common examples are phosphorylation, ubiquitination, Oxidation on methionine, deamidation (NQ).  Do not uses these examples unless there is evidence in the text to support them.",
           "prompts":
               [
                "In the following methods section of a paper, did they search for phosphorylation and any other post-translational modifications? Give just the answers with no other commentary.  The methods text is: [methods]    ",
                "Convert the following text, which was extracted from a proteomics study, into just a comma-separated list of all post-translational modifications (ptms) that are mentioned. Give no other commentary, only a list. The text is: [reply]"

                ],
                "dataOut": "ptms",
           "check": always_true}

prompt_data = [summarise, is_human, get_software, is_phospho, is_public, count_phospho, count_phospho_check, count_phospho_proteins, count_phospho_proteins_check, dia_query, settings_query, ptm_query]
