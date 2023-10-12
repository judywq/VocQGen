import spacy

nlp = spacy.load("en_core_web_sm")

def pos_check(inputs):
    word = inputs['word']
    tag = inputs['tag']
    sentence = inputs['sentence']
    
    doc = nlp(sentence)
    for token in doc:
        if token.text == word and token.tag_ == tag:
            return True
        
    return False
