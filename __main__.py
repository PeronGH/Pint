import sys
from parse_papers import parse_papers

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "config.csv"
    parse_papers(filename)
