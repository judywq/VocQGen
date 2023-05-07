from functools import reduce
import random
from typing import List, Optional
from lemminflect import getAllInflections

import logging
logger = logging.getLogger(__name__)


class ExtendableDict(dict):
    def extend(self, key, value: set):
        if key not in self.keys():
            self[key] = set()
        self[key].update(value)
    
    def merge(self, other: dict):
        for key, value in other.items():
            if key not in self.keys():
                self[key] = set()
            self[key].update(value)


class MyWord:
    def __init__(self, surface, tag=None) -> None:
        self.surface = surface
        self.tag = tag
    
    def __str__(self) -> str:
        return self.surface
    
    def __repr__(self) -> str:
        return f"{self.surface}<{self.tag}>"
    
    def __eq__(self, __value: object) -> bool:
        return self.tag == __value.tag and self.surface == __value.surface
    
    def __hash__(self) -> int:
        return hash((self.surface, self.tag))


class WordFamily:
    """A word family is a set of words that are related to each other.
        e.g. ['analyse', 'analyser', 'analysis', 'analyst']
        
        the list is extended with the inflections of each word, e.g.
        'analyse' -> ['analyse', 'analyses', 'analysed', 'analysing']
        
        the PoS tag of each word is also calulated and stored
    """
    def __init__(self, headword: str, related_words: Optional[List[str]]=None) -> None:
        self.tag_to_words = None
        self.all_words = set()
        # self.headword = headword
        self.construct(headword=headword, related_words=related_words)
        
    def __repr__(self) -> str:
        return f"WF: {self.headword}<{self.headword.tag}>"
    
    def construct(self, headword, related_words):
        self.tag_to_words = ExtendableDict()
        words = [headword]
        if related_words:
            words += related_words
        for i, word_surface in enumerate(words):
            self.tag_to_words.merge(self.get_all_inflections(word_surface))
            if i == 0:
                self.headword = next(filter(lambda w: w.surface==word_surface, 
                            [w for tmp_words in self.tag_to_words.values() for w in tmp_words]), "")
        if self.tag_to_words:
            self.all_words = reduce(lambda x, y: x.union(y), self.tag_to_words.values())
        else:
            self.all_words = set()
            
    def get_random_word(self, tag="*"):
        """get a random word from the word family with a given tag,
            if tag is *, return a random word from the whole family
        """
        candidates = []
        if tag == "*":
            candidates = list(self.all_words)
        else:
            candidates = list(self.tag_to_words.get(tag, []))
        if not candidates:
            logger.warning(f"No word found with tag <{tag}> in family <{self.headword}>")
            return ""
        return random.choice(candidates)
    
    @property
    def tags(self):
        return self.tag_to_words.keys()

    @staticmethod
    def get_all_inflections(word):
        """get all inflections of a word, return a map from tag to a set of inflections

        Args:
            word (str): an English word

        Returns:
            dict: a mapping from tag to a set of MyWord, e.g. 
                {'NN': {'account'},
                'NNS': {'accounts'},
                'VB': {'account'},
                'VBD': {'accounted'},
                ...}
        """
        res = getAllInflections(word)
        if not res:
            logger.warning(f"No inflections found for word: <{word}>")
        # convert the tuple into a set
        tag_to_words = {tag: set([MyWord(w, tag) for w in words]) for tag, words in res.items()}
        return tag_to_words
    
    def print(self):
        print("headword: <{}>\n{}".format(self.headword, self.tag_to_words))


class WordCluster:
    def __init__(self) -> None:
        self.tag_to_words = ExtendableDict()
        self.word_family_list = []
    
    def add_item(self, headword, related_words=[]):
        wf = WordFamily(headword, related_words)
        self.tag_to_words.merge(wf.tag_to_words)
        self.word_family_list.append(wf)
    
    def find_distractors(self, tag, excepts=[], n=10):
        words = self.tag_to_words.get(tag, set())
        # do not assign back to words, otherwise the original set will be modified
        candidates = words - set(excepts)
        
        if 0 <= n < len(candidates):
            # Use sample() instead of choices() to avoid duplicates
            return random.sample(list(candidates), k=n)
        else:
            return candidates
    
    @property
    def tag_size(self):
        return len(self.tag_to_words)
    
    @property
    def word_family_size(self):
        return len(self.word_family_list)
    
    def print(self):
        from pprint import pprint
        pprint(self.tag_to_words)


###################
# Test
###################
def test_word():
    w1 = MyWord('account', 'VB')
    w2 = MyWord('account', 'NN')
    w3 = MyWord('account', 'NN')
    print(w1)
    print(", ".join(str(w) for w in [w1, w2, w3]))
    s = {w1, w2, w3}
    print(s)
    
def test_family():
    wf = WordFamily('analyse', ['analyser', 'analysis', 'analyst'])
    wf.print()
    print(wf.get_random_word(tag='*'))
    

def test_cluster():
    wc = WordCluster()
    wc.add_item('analyse', ['analyser', 'analysis'])
    wc.print()
    wc.add_item('approach', ['approachable'])
    wc.print()

    
if __name__ == '__main__':
    test_word()
    test_family()
    # test_cluster()
