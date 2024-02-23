from os.path import dirname, abspath
import sys
 
directory = dirname(dirname(abspath(__file__)))
# https://www.geeksforgeeks.org/python-import-from-parent-directory/
sys.path.append(directory)


from lib.ngram import filter_high_freq_inflections, search_ngram, filter_high_freq_pos


def test_search():
    content = "account_*"
    res = search_ngram(content=content)
    print(res)


def test_pos_filtering():
    w = 'account'
    pos_list = ['NN', 'VB', 'VBZ', 'JJ']
    res = filter_high_freq_pos(headword=w, pos_list=pos_list, th=0.1)
    print(res)


def test_inflection_filtering():
    inf_data = {
        'NN': {'account'},
        'NNS': {'accounts'}
    }
    inf_data = {
        'NN': {'fish'},
        'NNS': {'fishes'}
    }
    res = filter_high_freq_inflections(inf_data=inf_data, th=0.1)
    print(res)

if __name__ == "__main__":
    # test_pos_filtering()
    test_inflection_filtering()
