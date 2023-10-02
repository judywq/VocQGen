from collections import defaultdict
from lemminflect import getAllInflections
from unimorph import inflect_word

import logging
logger = logging.getLogger(__name__)

# https://unimorph.github.io/doc/unimorph-schema.pdf
unimorph_to_penn = {
    'N;SG': 'NN',
    'N;PL': 'NNS',
    'V;NFIN;IMP+SBJV': 'VB',
    'V;PST': 'VBD',
    'V;V.PTCP;PRS': 'VBG',
    'V;V.PTCP;PST': 'VBN',
    'V;PRS;3;SG': 'VBZ',
    'ADJ': 'JJ',
    'ADJ;CMPR': 'JJR',
    'ADJ;SPRL': 'JJS',
    'ADV': 'RB',
    'ADV;CMPR': 'RBR',
    'ADV;SPRL': 'RBS',
    'PRON': 'PRP',
    'DET': 'DT',
    'PREP': 'IN'
}

# Function to convert Unimorph tags to Penn Treebank POS tags
def convert_unimorph_to_penn(unimorph_tag):
    return unimorph_to_penn.get(unimorph_tag, 'UNK')  # 'UNK' for unknown tags


def get_inflections(word):
    """get all inflections of a word, return a map from tag to a set of inflections

    Args:
        word (str): an English word

    Returns:
        dict: a mapping from tag to a set of words, e.g. 
            {'NN': {'account'},
            'NNS': {'accounts'},
            'VB': {'account'},
            'VBD': {'accounted'},
            ...}
    """
    tag_to_words_lemm = get_inflections_lemm(word)
    tag_to_words_unimorph = get_inflections_unimorph(word)
    
    res = {}
    for key, value in tag_to_words_lemm.items():
        inter = value & tag_to_words_unimorph.get(key, set())
        if inter:
            res[key] = inter
    res = get_correct_inflections(res)

    # create a dict that logs the differences
    total_keys = set(tag_to_words_lemm.keys()) | set(tag_to_words_unimorph.keys())
    full_log = []
    for tag in total_keys:
        total_values = tag_to_words_lemm.get(tag, set()) | tag_to_words_unimorph.get(tag, set())
        for w in total_values:
            full_log.append({
                         "word": w,
                         "tag": tag,
                         "lemm": w in tag_to_words_lemm.get(tag, set()),
                         "unimorph": w in tag_to_words_unimorph.get(tag, set()),
                         "final": w in res.get(tag, set()),
                         })
    return res, full_log


def get_correct_inflections(tag_to_words: dict):
    """Corret the inflections of a word based on the following rules:
        1. word (NN), words (NNS) [OK, do nothing]
        2. finance (NNS) -> finance (NN)
        3. structure (NN), structure (NNS) -> structure (NN)
        4. method (NN), method (NNS), methods(NNS) -> method (NN), methods(NNS)

    Args:
        tag_to_words (dict): a mapping from tag to a set of words

    Returns:
        dict: corrected mapping from tag to a set of words
    """
    tags = tag_to_words.keys()
    has_NNS = 'NNS' in tags
    has_NN = 'NN' in tags
    
    if has_NNS and not has_NN:
        # NNS only -> Replace it with NN
        tag_to_words['NN'] = tag_to_words['NNS']
        del tag_to_words['NNS']
    elif has_NNS and has_NN:
        # Remove NN from NNS
        tag_to_words['NNS'] -= tag_to_words['NN']
        if (len(tag_to_words['NNS']) == 0):
            del tag_to_words['NNS']
    return tag_to_words


def get_inflections_lemm(word):
    res = getAllInflections(word)
    if not res:
        logger.warning(f"No inflections found for word: <{word}>")
    # convert the tuple into a set
    tag_to_words = {tag: set([w for w in words]) for tag, words in res.items()}
    return tag_to_words


def get_inflections_unimorph(word):
    res = inflect_word(word, lang="eng")
    tag_to_words = defaultdict(set)
    for line in res.split("\n"):
        if not line:
            continue
        orig, surface, unimorph_tag = line.split('\t')
        tag = convert_unimorph_to_penn(unimorph_tag)
        if surface == 'countable' or surface == 'uncountable':
            surface = orig
        tag_to_words[tag].add(surface)
    return dict(tag_to_words)

