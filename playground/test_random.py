import random

random.seed(42)

def take():
    print(random.choices([1,2,3,], k=3))
    # randomly select n elements from list
    print(random.sample([1,2,3,], k=3))

def test():
    take()
    # take()

if __name__ == '__main__':
    test()
    
