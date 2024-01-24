from pprint import pprint
from lib.chat import MyBotWrapper
from lib.dict_helper import get_senses_of_keyword
from lib.parser import SenseRankParser


def test_sense_rank():
    keyword = 'contract'
    bot = MyBotWrapper(parser=SenseRankParser(), temperature=0)
    sense_map = get_senses_of_keyword(keyword)
    # tag, senses = next(iter(sense_map.items()))
    
    tag = 'VB'
    senses = sense_map.get(tag)
    
    print(tag)
    pprint(senses)
    print(10*'-')
    # return
        
    res = bot.run(inputs={"keyword": keyword, "tag": tag, "senses": senses})
    pprint(res.get('result', 'NO RESULT'))
    
    
if __name__ == '__main__':
    test_sense_rank()