Pubmed integrated NLP tool:  For serial processing of open-source PubMed Central papers with an LLM (openai, anthropic's claude or external shell script are supported)

Configuration is via the Excel file
Run with 'python run_pint.py <config file>'
The config file sets many options - the model to use, where to find the data and the prompts, as well as other settings.

Input is a csv or Excel file with a specified column - either a pubmed id or a filename (assumed if it's not numerical or PMC)
Output is a csv file with the id and the requested data 

There is a simple example in the example folder which uses .pdf files
cd example
python ../run_pint.py test_config_pdf.xlsx


You can use .csv files in place of .xlsx files - it's just harder to keep the documents nicely formatted.



