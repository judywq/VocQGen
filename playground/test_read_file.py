
from os.path import dirname, abspath
import sys
 
directory = dirname(dirname(abspath(__file__)))
# https://www.geeksforgeeks.org/python-import-from-parent-directory/
sys.path.append(directory)

# import lib.io
from lib.io import read_data


def test():
    path = "data/input/AWL.xlsx"
    df = read_data(path)
    # print(df.head())
    for index, row in df.iterrows():
        related_words = row['Related word forms'].split(',')
        print(row['Headword'], related_words)
        break

if __name__ == '__main__':
    test()
    