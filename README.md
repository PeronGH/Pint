Pubmed integrated NLP tool:  For serial processing of open-source PubMed Central papers with an LLM (openai, anthropic's claude or external shell script are supported)

Configuration is via the Excel file
Run with 'python RunPint.py test_config.xlsx'
Input is a csv or Excel file with a pubmed id column
Output is a csv file with the pubmed id and the requested data (see test_prompts.xlsx, referenced in test_config.xlsc for how this is requested)

This example looks at papers that may be related to the Plasmodium Falciparum gene PF3D7_0102500 - (EBA-181 or JESEBL), and outputs the role found by the prompts.


