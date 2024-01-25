# https://www.guru99.com/pos-tagging-chunking-nltk.html#:~:text=POS%20Tagging%20in%20NLTK%20is,each%20word%20of%20the%20sentence.
# This only works if the word is in a sentence, it is not suitable for outputing all the pos of a word

from os.path import dirname, abspath
import sys
directory = dirname(dirname(abspath(__file__)))
# https://www.geeksforgeeks.org/python-import-from-parent-directory/
sys.path.append(directory)

from lib.nlp_helper import pos_check



def test_nltk_tag():
    from nltk import pos_tag
    from nltk import RegexpParser

    text ="learn php from guru99 and make study easy".split()
    print("After Split:",text)
    tokens_tag = pos_tag(text)
    print("After Token:",tokens_tag)
    patterns= """mychunk:{<NN.?>*<VBD.?>*<JJ.?>*<CC>?}"""
    chunker = RegexpParser(patterns)
    print("After Regex:",chunker)
    output = chunker.parse(tokens_tag)
    print("After Chunking",output)

    output.draw()
    # pos_tag("I have a report to report".split())
    

def test_pos_check():
    word = 'labor'
    tag = 'VB'
    sentence = 'Many workers labor tirelessly to ensure our city remains clean and orderly throughout the year.'
    
    word = 'constitutional'
    tag = 'NN'
    sentence = 'Every morning, she takes her dog for a/an constitutional in the peaceful city park.'
    
    res = pos_check(inputs={'word': word, 'tag': tag, 'sentence': sentence})
    print(res)
    

if __name__ == '__main__':
    test_pos_check()