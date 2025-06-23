import sys

def main():
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.csv"

 
    from .parse_papers import parse_papers
    parse_papers(config_file)

if __name__ == "__main__":
    main()