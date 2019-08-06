'''
interpolation-module
Created on 19 may. 2018
@author: AMG
'''
import numpy as np
def resampleandinterpolate(df,mininterval,c):
    dfreturn = df.resample(str(mininterval) + 'T').mean()
    dfreturn['quality'] = dfreturn['quality'].fillna(c.interqc)
    dfreturn = dfreturn.interpolate()
    return dfreturn
def interpolate(originaldf,intervalinterpolate,mininterval,logger,config,c):
    logger.info('Interpolation - qc interpolation >> started!')
    #properties
    maxgapinminutes = int(config['interpolation']['maxgapinminutes']) # Max allowed gap in minutes
    subsamplingmethod = config['interpolation']['subsamplingmethod'] # mean, first(default)
    #logic
    df = originaldf.copy()
    if intervalinterpolate == None:
        intervalinterpolate = str(mininterval) + 'T'
    else:
        intervalinterpolate = str(intervalinterpolate) + 'T'
    #bad data values are dropped
    df = df[df.quality != c.badqc]
    #for each fragment (gaps smaller than maxgapinminutes) resample and interpolate
    targetdf = df[df.quality == c.badqc]
    ini=0
    for ix in range(1,len(df.index.values)):
        if df.index.values[ix] - df.index.values[ix-1] > np.timedelta64(maxgapinminutes, 'm'):
            end = ix
            targetdf = targetdf.append(resampleandinterpolate(df[ini:end],mininterval,c))
            ini = ix
    end = len(df.index.values)
    targetdf = targetdf.append(resampleandinterpolate(df[ini:end],mininterval,c))
    targetdf = targetdf.resample(str(mininterval) + 'T').mean()
    targetdf['quality'] = targetdf['quality'].fillna(c.nullqc)
    if subsamplingmethod == 'mean':
        targetdf = targetdf.resample(intervalinterpolate).mean()
    else:
        targetdf = targetdf.resample(intervalinterpolate).first()
    
    # to avoid NaNs when interval to interpolate is minor than series original interval    
    if mininterval > int(intervalinterpolate[:-1]):
        targetdf = targetdf.interpolate()
    
    targetdf = targetdf.drop('quality', 1)
    return targetdf