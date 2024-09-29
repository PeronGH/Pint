import traceback
import csv
import requests
import os
import json
import subprocess
from types import SimpleNamespace

from parse_pubmed_json import parse_pubmed_data
from prompt_data import prompt_data

# - The things you are likely so set are here
# ** prompt_data.py ** is where all of the prompts, checks and structure is defined

# "claude" or "openai"
WHICH_API = "claude"
USE_PUBMED_API = True
# You can either pass the key as text, ("sk-proj...") or if None, it will look for an environment variable
# ANTHROPIC_API_KEY or OPENAI_API_KEY
API_KEY = None

file_path = 'data/Human phosphorylation datasets 2024.csv'
column_name = 'pubmed_id'  # Name of the column containing PubMed IDs
# The pubmed sections to extract - if None, it will extract all
sections_to_extract = ["abstract",  "intro", "methods", "results", "discuss",]

# The output file name is based on the input file name just for convenience
output_file = file_path + '_output.csv'  # Path to the output CSV file
output_file_json = file_path + '_output.json'  # Path to the output CSV file

debug_output_file = file_path + '_output_debug.csv'  # Path to the output CSV file
debug_output_file_json = file_path + '_output_debug.json'  # Path to the output CSV file

# You can either pass the key as text, (key="sk-proj...") or it will look for an environment variable
if WHICH_API == "claude":
    from claudeEngine import ClaudeEngine
if WHICH_API == "openai":
    from openAIEngine import OpenAIEngine


# Responses are stored so that they are not repeated later
# If you want to clear the cache, delete the cache folder, or you can change the key in the specific api file

data_folder = 'pubmed_data'
cache_folder = 'api_cache'

self_data =  SimpleNamespace()

self_data.data_store = {}
self_data.output_data = {}
self_data.final_output = {}
self_data.debug = {}
print("starting...")

def setup():
    if WHICH_API == "claude":
        self_data.llm_engine = ClaudeEngine(
        key=API_KEY, cache_folder=cache_folder)
    if WHICH_API == "openai":
        self_data.llm_engine = OpenAIEngine(key=API_KEY, cache_folder=cache_folder)
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(cache_folder, exist_ok=True)
 

def process_line(line):
    system = line["system"]

    check = line["check"]
    name = line["name"]
    preCheck = None
    if "preCheck" in line:
        preCheck = line["preCheck"]

    for prompt in line["prompts"]:
        full_prompt = prompt
        for key in self_data.data_store:
            full_prompt = full_prompt.replace(f"[{key}]", self_data.data_store[key])

        skipStage = False
        # If there is a preCheck, it will return True if the stage should be skipped
        if preCheck:
            skipStage = preCheck(self_data.data_store["reply"])


        if skipStage:
            result = self_data.data_store["reply"]
        else:
            result = self_data.llm_engine.prompt(full_prompt, system)

        self_data.data_store["reply"] = result
        self_data.reply_count += 1
        self_data.data_store[f"reply_{self_data.reply_count}"] = result

    answer = check(result)

    # The check may have modified the reply - for example removing commas from numbers

    if answer:
        self_data.data_store["reply"] = answer
        result = answer

    if "putVariable" in line:
        out = line["putVariable"]
        self_data.data_store[out] = result

    if "dataOut" in line:
        out = line["dataOut"]
        self_data.output_data[out] = result



    if not "hide" in line:
        print(f"{name}: {answer}")
    return answer


def process_document(pmid,document_data):

    text = document_data["text"]
    sections = document_data["sections"]

    result = None
    self_data.reply_count = 0
    self_data.output_data = {}
    self_data.data_store = {"paper": text}
    for section in sections:
        self_data.data_store[section] = sections[section]

    print(f"Processing {pmid}")
    for process in prompt_data:

        result = process_line(process)

        if result is None:
            break

    if result is not None:
        result = self_data.output_data.copy()
    self_data.debug[pmid] = self_data.data_store.copy()

    return result

def get_pubmed_from_local(pubmed_id):
    script_path ="/mnt/hc-storage/groups/cbf/tony/share/pubmed/get_pmid"

    #call an external script to get the data, passing in the pubmed id
    data = []
    try:
        data = subprocess.check_output([script_path, pubmed_id])
        data = json.loads(data)
    except subprocess.CalledProcessError as e:
        print("Error",e)

    return data


def get_pubmed_from_api(pubmed_id):
    api_url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/" + str(pubmed_id) + "/unicode"

    data = []
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        data = response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")

    return data

# Function to fetch PubMed data via API or from a local file
def fetch_pubmed_data(pubmed_id, sections_to_extract, data_folder):

    json_file_path = os.path.join(data_folder, f"{pubmed_id}.json")

    # Check if the JSON file already exists, to cache it
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    else:
        # Fetch the data from PubMed API (alternative is a local script)
        if USE_PUBMED_API:
            data = get_pubmed_from_api(pubmed_id)
        else:
            data = get_pubmed_from_local(pubmed_id)

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    # Extract the relevant sections from the JSON data

    parsed_data = parse_pubmed_data(data, sections_to_extract)


    return parsed_data




# Function to process each PubMed ID
def process_pubmed_id(pubmed_id, processed_documents, sections_to_extract, data_folder):
    document_data  = fetch_pubmed_data(pubmed_id, sections_to_extract, data_folder)
    document_text = document_data.get("text")

    if document_text:
        if len(document_text) > 1:
            processed_documents.append(document_text)
            result = process_document(pubmed_id,document_data)
            if result:
                self_data.final_output[pubmed_id] = result

def normalize_newlines(text):
    if isinstance(text, str):
        text = text[:10000]
        text = text.replace('\"', '')


        text= text.replace('\r', '')
        return text.replace('\n', ' \\n ')
    return text
def output_csv(output_data,outputfile):
    columns = set()
    for key in output_data:
        columns.update(output_data[key].keys())

    # Convert the set to a sorted list to maintain column order
    columns = sorted(columns)

    # Step 2: Write to CSV
    with open(outputfile, 'w', newline='', encoding='utf-8' ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[column_name] + columns,quoting=csv.QUOTE_ALL)
        writer.writeheader()

        # Step 3: Write data rows
        for key, values in output_data.items():
            row = {column_name: key}  # Start row with the main key
            row.update(values)  # Update the row with the nested dictionary
            normalized_row = {k: normalize_newlines(v) for k, v in row.items()}

            writer.writerow(normalized_row)


# Function to read CSV and extract PubMed IDs from a specific column
def process_pubmed_ids_from_csv(file_path, column_name, sections_to_extract, data_folder):
    processed_documents = []  # List to store processed documents

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if column_name not in reader.fieldnames:
                raise ValueError(f"Column '{column_name}' not found in the CSV file.")

            for row in reader:
                pubmed_id = row[column_name]
                if pubmed_id:
                    if int(pubmed_id) > 0:
                        process_pubmed_id(pubmed_id, processed_documents, sections_to_extract, data_folder)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

    print("Final Output")
    print(self_data.final_output)

    output_csv(self_data.final_output,output_file)
    #write the final output to a file output_file_json
    with open(output_file_json, 'w') as json_file:
        json.dump(self_data.final_output, json_file, indent=4)

#    print(self_data.debug)
    output_csv(self_data.debug,debug_output_file)
    #write the final output to a file output_file_json
    with open(debug_output_file_json, 'w') as json_file:
        json.dump(self_data.debug, json_file, indent=4)


    return processed_documents


def parse_papers():

    setup()
    # Get the list of processed documents
    processed_documents = process_pubmed_ids_from_csv(file_path, column_name, sections_to_extract, data_folder)
    print(f"Processed {len(processed_documents)} documents.")
