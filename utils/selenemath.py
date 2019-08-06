'''
selenemath-util
Created on 19 may. 2018
@author: AMG
'''
import numpy as np
def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean()) 
