from pprint import pprint
from lib.inflections import get_inflections


def main():
    word = "get"
    tag_to_words, full = get_inflections(word)
    pprint(tag_to_words)
    pprint(full)

if __name__ == "__main__":
    main()
    