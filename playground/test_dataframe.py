import pandas as pd
import sys
import os

#  https://www.geeksforgeeks.org/python-import-from-parent-directory/
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from lib.io import write_data

def test_col_size():
    col = ['a', 'b', 'c']
    SIZE = len(col)
    data = []
    row = [1,2]
    row += [None] * (SIZE - len(row))
    data.append(row)
    data.append([1,2])
    # data.append([1,2,3])
    # data.append([1,2,3,4][:len(col)])
    df = pd.DataFrame(data=data, columns=col)
    
    write_data(df, 'data/output/test.xlsx')
    print(df)
    

if __name__ == '__main__':
    test_col_size()
    