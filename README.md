Pubmed integrated NLP tool:  For serial processing of open-source PubMed Central papers with an LLM (openai or claude supported)
Input is a csv file with a pubmed id column
Output is a csv file with the pubmed id and the requested data (see prompt_data.py for how this is requested)

This example looks for phosphorylation related attributes, and outputs the results.

prompt_data.py contains the settings and the prompting structure.
