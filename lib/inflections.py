from collections import defaultdict
from lemminflect import getAllInflections
from unimorph import inflect_word
from lib.dict_helper import get_pos_list_of_keyword, translate_fl_to_pos
from lib.utils import get_general_pos
from lib.parser import PosRankParser
from lib.chat import MyBotWrapper
from lib.ngram import filter_high_freq_inflections, filter_high_freq_pos

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


def get_inflections(headword):
    """get all inflections of a word, return a map from tag to a set of inflections
    
    1. Get all POS tags from dictionary
    2. Filter out unimportant POS tags using GPT
    3. Get the union of inflections from lemm and unimorph
    4. Take the intersection of the union (step 3) with the result of step 2
    5. If the result is empty, simply use the dictionary form
    6. If the result is still empty, try use the intersection of the two sets

    Args:
        headword (str): an English word

    Returns:
        dict: a mapping from tag to a set of words, e.g. 
            {'NN': {'account'},
            'NNS': {'accounts'},
            'VB': {'account'},
            'VBD': {'accounted'},
            ...}
    """
    
    tag_to_words_lemm = get_inflections_lemm(headword)
    tag_to_words_unimorph = get_inflections_unimorph(headword)
    # create a dict that logs the differences
    total_keys = set(tag_to_words_lemm.keys()) | set(tag_to_words_unimorph.keys())
        
    # 1. Get all POS tags from dictionary
    pos_list = get_pos_list_of_keyword(headword)
    if not pos_list:
        logging.warning(f"Cannot find POS for word: <{headword}>, please check the word is fetched from the dictionary.")
        pos_list = []
    
    # 2. Filter out unimportant POS tags using GPT
    bot = MyBotWrapper(parser=PosRankParser(), temperature=0)
    r = bot.run(inputs={'keyword': headword, 'tags': pos_list})
    top_pos_list = r.get('result', [])
    top_pos_list = [translate_fl_to_pos(tag) for tag in top_pos_list]
    
    total_keys |= set(top_pos_list)

    # 3. Take the union of the two sets
    res = {}
    all_tags = set(tag_to_words_lemm.keys()) | set(tag_to_words_unimorph.keys())
    for tag in all_tags:
        tmp_union = tag_to_words_lemm.get(tag, set()) | tag_to_words_unimorph.get(tag, set())
        if tmp_union:
            res[tag] = tmp_union    
    
    # 4. Filter the union by the top_pos_list
    res = filter_inflections_by_pos(res, top_pos_list)

    # 5. If the final result is empty, simply use the dictionary form
    if len(res) <= 0:
        for tag in top_pos_list:
            res[tag] = {headword}
    
    # 6. If the result is still empty, try use the intersection of the two sets
    if len(res) <= 0:
        for key, value in tag_to_words_lemm.items():
            inter = value & tag_to_words_unimorph.get(key, set())
            if inter:
                res[key] = inter

    # 7. Correct the inflections (especially NN, NNS)
    res = get_correct_inflections(res)
    
    # 8. Keep only high frequency POS tags
    res = try_filter_high_freq_pos(headword, res)
    ngram_pos = list(res.keys())
    
    before_noun_ngram_pos = set(res.keys())
    # 9. Keep only high frequency NN, NNS
    res = try_filter_high_freq_noun(res)
    noun_removed = list(before_noun_ngram_pos - set(res.keys()))

    full_log = []
    if len(total_keys) <= 0:
        full_log.append({
                         "headword": headword,
                         "word": w,
                         "tag": '-',
                         "lemm": '-',
                         "unimorph": '-',
                         "dict_pos": ",".join(pos_list),
                         "gpt_pos": ",".join(top_pos_list),
                         "ngram_pos": ",".join(ngram_pos),
                         "noun_removed": ",".join(noun_removed),
                         "final": '-',
                         })
    for tag in total_keys:
        total_values = tag_to_words_lemm.get(tag, set()) | tag_to_words_unimorph.get(tag, set())
        total_values |= res.get(tag, set())
        for w in total_values:
            full_log.append({
                         "headword": headword,
                         "word": w,
                         "tag": tag,
                         "lemm": w in tag_to_words_lemm.get(tag, set()),
                         "unimorph": w in tag_to_words_unimorph.get(tag, set()),
                         "dict_pos": ",".join(pos_list),
                         "gpt_pos": ",".join(top_pos_list),
                         "ngram_pos": ",".join(ngram_pos),
                         "noun_removed": ",".join(noun_removed),
                         "final": w in res.get(tag, set()),
                         })
    return res, full_log


def filter_inflections_by_pos(tag_to_words: dict, pos_list: list[str]):
    def is_pos_in_list(tag: str, pos_list: list[str]):
        for pos in pos_list:
            general_tag = get_general_pos(tag)
            if general_tag == pos:
                return True
        return False
    
    result = {}
    for tag, words in tag_to_words.items():
        if is_pos_in_list(tag, pos_list):
            result[tag] = words
    return result


def get_correct_inflections(tag_to_words: dict):
    """Corret the inflections of a word based on the following rules:
        1. word (NN), words (NNS)  # OK, do nothing
        2. finance (NNS) -> finance (NN)  # Plural (NNS) only, replace it with NN
        3. structure (NN), structure (NNS) -> structure (NN)  # NN and NNS with same form, keep NN only
        4. method (NN), method (NNS), methods(NNS) -> method (NN), methods(NNS)  # Multiple NNS, remove NN-form NNS

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


def try_filter_high_freq_pos(headword, tag_to_words: dict):
    """Filter the inflections by general POS tags

    Args:
        headword (str): the headword of the word family
        tag_to_words (dict): a mapping from tag to a set of words

    Returns:
        dict: filtered mapping from tag to a set of words
    """
    pos_list = list(tag_to_words.keys())
    if len(pos_list) <= 1:
        # No need to filter if there is only one POS tag
        return tag_to_words
    
    filtered_pos_list = filter_high_freq_pos(headword=headword, pos_list=pos_list)
    result = {}
    for tag, words in tag_to_words.items():
        general_tag = get_general_pos(tag)
        if general_tag in filtered_pos_list:
            result[tag] = words
    return result


def try_filter_high_freq_noun(tag_to_words: dict):
    """Filter the NN, NNS inflections of a word family by high frequency POS tags, keep only high frequency POS tags

    Args:
        tag_to_words (dict): a mapping from tag to a set of words

    Returns:
        dict: filtered mapping from tag to a set of words
    """
    noun_tag_to_words = {}
    other_tag_to_words = {}
    for tag, words in tag_to_words.items():
        general_tag = get_general_pos(tag)
        if general_tag == 'NN':
            noun_tag_to_words[tag] = words
        else:
            other_tag_to_words[tag] = words
    
    if len(noun_tag_to_words) <= 1:
        # No need to filter if there is only one noun tag
        return tag_to_words
    
    result = filter_high_freq_inflections(noun_tag_to_words, th=0.1)
    # result = {**result, **other_tag_to_words}
    result.update(other_tag_to_words)
    return result

def get_inflections_lemm(word):
    res = getAllInflections(word)
    # if not res:
        # logger.warning(f"No inflections found for word: <{word}>")
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

