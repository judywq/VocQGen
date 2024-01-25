from lib.dict_helper import *
from lib.dict_helper import _try_get_american_spelling
import setting
from pprint import pprint
import logging

api_key = setting.DICT_API_KEY

def test_fetch():
    logging.basicConfig(level=logging.DEBUG)
    
    # keywords = ['account', 'finance', 'structure', 'method', 'test']
    # keywords = ['account']
    keywords = ['conceptualise']
    result = fetch_words_from_dict(keywords=keywords, api_key=api_key)
    pprint(len(result))
    
def test_senses():
    keyword = 'contract'
    keyword = 'policy'
    res = get_senses_of_keyword(keyword)
    pprint(res)
    senses = res.get('NN', [])
    print("\n".join(senses))
    

def test_remove_tag():
    from lib.utils import remove_curly_braces_content
    # Example usage
    input_string = '{bc}a record of debit {dx_def}see {dxt|debit:2||1a}{/dx_def} and '
    result = remove_curly_braces_content(input_string)
    print(result)


def test_spelling():
    word = 'analyse'
    # json_data = try_load_from_json(word)
    # res = get_senses_of_keyword(word)
    res = get_pos_list_of_keyword(word)
    # res = _try_get_american_spelling(word)
    print(res)

    

if __name__ == '__main__':
    # test_fetch()
    test_senses()
    # test_remove_tag()
    # test_spelling()