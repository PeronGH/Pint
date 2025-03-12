import sys
from model_data import load_model_data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.csv"
    load_model_data(config_file)

 
    from parse_papers import parse_papers
    parse_papers()