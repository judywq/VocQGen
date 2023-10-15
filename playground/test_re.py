import re

def search(sentence, word, expected):
    pat = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
    if bool(pat.search(sentence)) == expected:
        print("OK.")
    else:
        print("Not OK.")

def test_search():
    tests= [
        ('The university aims to preserve its longstanding ______ by organizing an annual cultural festival that showcases various traditional arts and performances.', 'tradition', False),
        ('This is a tradition.', 'tradition', True),
        ('This is a tradition blah.', 'tradition', True),
    ]
    for sentence, word, expected in tests:
        search(sentence, word, expected)
        
if __name__ == '__main__':
    test_search()
    