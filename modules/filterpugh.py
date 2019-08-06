'''
filterhandler-module
Created on 23 may. 2018
@author: AMG
'''
import utils.iofilehandler as iofilehandler
import datetime
import numpy as np
def filt(df,logger,c):
    logger.info('Filter - Pugh filterhandler >> started!')
    #pughrules
    taps = np.asarray(iofilehandler.filterwindow(c.pughtaps)).astype(np.float)
    filtered = []
    for t in range(0,len(df['data'])):
        if t-len(taps) < 0 or t+len(taps) > len(df['data']):
            filtered.append(np.NaN)
        else:
            summation = 0
            for m in range(1,len(taps)):
                summation = summation + taps[m] * (df['data'][t+m] + df['data'][t-m])
            filtered.append(round((taps[0] * df['data'][t] + summation) * 100) / 100)
    df['data'] = filtered
    df = df.resample('1H').first()
    #first element after gap is removed
    ixnan=np.where(np.isnan(df['data']))[0]
    diff = np.diff(ixnan)
    endgap = np.where(diff > 1)
    for i in endgap:
        df.iloc[ixnan[i]+1] = np.nan
    return df
