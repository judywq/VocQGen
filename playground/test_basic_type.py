def test_dict():
    d = {'a': 1, 'b': 2}
    res = {
        **d,
        'a': 3,
    }
    print(res)
    
if __name__ == '__main__':
    test_dict()
    