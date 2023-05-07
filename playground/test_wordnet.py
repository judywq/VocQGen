# https://www.nltk.org/howto/wordnet.html
# words like 'at', 'the' are not included in the wordnet databse

from nltk.corpus import wordnet as wn

def test_synsets():
    dog0 = wn.synset('dog.n.01')
    dog0.definition()

    wn.synsets('dog', pos=wn.VERB)
    # wn.langs()
    # wn.synsets(b'\xe7\x8a\xac'.decode('utf-8'), lang='jpn')
    # wn.synset('spy.n.01').lemma_names('jpn')

    wn.synset('dog.n.01').lemmas()


def explain(word):
    for s in wn.synsets(word):
        exe = s.examples()[0] if len(s.examples()) > 0 else "(no_ex.)"
        fields = [
            s.pos(), 
            s.name(), 
            s.definition(), 
            exe, 
            s.lemmas(),
            ]
        SEP = ' | '
        print(SEP.join(map(str, fields)))

explain('eat')
explain('above')

