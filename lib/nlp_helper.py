import spacy
import string

# python -m spacy download en_core_web_sm  # <-- run first time
nlp = spacy.load("en_core_web_sm")

def pos_check(inputs):
    word = inputs['word']
    tag = inputs['tag']
    sentence = inputs['sentence']
    
    doc = nlp(sentence)
    for token in doc:
        # print(token.tag_, token.text)
        if token.text == word and token.tag_ == tag:
            return True
        
    return False


def is_good_position(sentence, keyword):
    """Check if the keyword is in a good position in the sentence
    
    Args:
        sentence (str): sentence to check
        keyword (str): keyword to check
    
    Returns:
        bool: True if the keyword is in a good position
    """
    
    def remove_punctuation(s):
        return s.translate(str.maketrans('', '', string.punctuation))
    
    sentence = remove_punctuation(sentence.lower())
    keyword = remove_punctuation(keyword.lower())
    
    # Check if the keyword is in the beginning of the sentence
    if sentence.startswith(keyword):
        return False
    
    # Check if the keyword is in the end of the sentence
    if sentence.endswith(keyword):
        return False
    
    return True


def test_position():
    word = 'data'
    sentence = 'Data is a plural noun.'
    sentence = 'Give me the data.'
    sentence = 'The data is not available.'
    
    print(is_good_position(sentence, word))

if __name__ == '__main__':
    test_position()
    