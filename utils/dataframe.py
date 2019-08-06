'''
dataframe-util
Created on 7 jun. 2018
@author: AMG
'''
import numpy as np
def mininterval(df):
    intervals = [df.index.values[i + 1] - df.index.values[i] for i in range(len(df.index.values)) if i+1 < len(df.index.values)]
    return int(min(intervals).astype('timedelta64[m]') / np.timedelta64(1,'m'))
def save(df,filename):
    df.to_csv(filename, header=None, index=True, sep=' ', mode='w')
    return None