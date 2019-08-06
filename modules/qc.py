'''
qc-module
Created on 19 may. 2018
@author: AMG
'''
import time
import utils.selenemath as smath
import numpy as np
import warnings
def qc(originaldf,nsigma,winsize,splinedegree,stucklimit,max,min,logger,c):
    logger.info('Quality control - qc module >> started!')
    t = time.time()
    #nsigma: Number of sigmas to identify an event
    #winsize: Number of data of the window to fit the spline
    #splinedegree: Degree of the spline
    #stucklimit: Steps with same value to consider stucked value
    warnings.simplefilter('ignore', np.RankWarning)
    #qc.py:63: RankWarning: Polyfit may be poorly conditioned splinefit = np.polyfit(winx, windata, splinedegree)
    df = originaldf.copy()
    badixs = []
    logger.debug('Original dataframe number of elements:' + str(len(df))) 
    #drop originally bad values
    df = df[df.quality != c.badqc]
    logger.debug('Drop bad data. Dataframe number of elements:' + str(len(df))) 
    logger.debug('Quality control - TIME to clean bad data - qc module: ' + str(time.time() - t) + ' seconds')
    t = time.time()
    #stuck test and range (max-min) test
    stuckcount = 1
    stuckvalue = None
    for ix in range(len(df.index.values)):
        #stuck
        if df['data'][ix] == stuckvalue:
            stuckcount = stuckcount+1
            if stuckcount == stucklimit:
                for i in range(0,stucklimit-1):
                    df.loc[df.index.values[ix-i],'quality'] = c.badqc
                    badixs.append(df.index.values[ix-i])
            elif stuckcount > stucklimit:
                df.loc[df.index.values[ix],'quality'] = c.badqc
                badixs.append(df.index.values[ix])
            else:
                pass
        else:
            stuckvalue = df['data'][ix]
            stuckcount = 1
        #max-min
        if df['data'][ix] > max or df['data'][ix] < min:
            df.loc[df.index.values[ix],'quality'] = c.badqc
            badixs.append(df.index.values[ix])
    #drop stucked and out of range (between max min) values
    df = df[df.quality != c.badqc]
    logger.debug('Drop stuck data and out of range (max-min) data. Dataframe number of elements:' + str(len(df)))
    logger.debug('Quality control - TIME to check stuck values and out of range (max-min) values and clean bad data detected - qc module: ' + str(time.time() - t) + ' seconds')
    #spiketest    
    spikedetected = True
    iter = 0
    while spikedetected and iter < c.maxiter:
        #drop spike values detected in previous iteration
        df = df[df.quality != c.badqc]
        logger.debug('Spike iteration. Dataframe number of elements:' + str(len(df))) 
        spikedetected = False
        t = time.time()
        for ix in range(len(df.index.values)):
            if (ix < winsize/2):
                ini=0
                end=winsize-1
                winix = ix
            elif (ix > len(df.index) - winsize/2):
                ini=len(df.index)-winsize
                end=len(df.index)-1
                winix = (winsize-1)-(end-ix+1)
            else:
                ini = int(ix - winsize/2)
                end = int(ix + winsize/2)
                winix = int(winsize/2)
            winx = df.index.values[ini:end].astype(float)
            windata = df['data'].values[ini:end]
            splinefit = np.polyfit(winx, windata, splinedegree)
            splinedata = np.polyval(splinefit,winx)
            rmse = smath.rmse(splinedata, np.array(windata))
            if (abs(splinedata[winix]-df['data'][ix]) >= nsigma*rmse):
                df.loc[df.index.values[ix],'quality'] = c.badqc
                badixs.append(df.index.values[ix])
                spikedetected = True
        logger.debug('Quality control - TIME to spike test loop - qc module: ' + str(time.time() - t) + ' seconds')
        iter=iter+1
    #after quality control process all data (excepting previously marked as bad data) are set to good data
    originaldf.loc[originaldf['quality'] != c.badqc, 'quality'] = c.goodqc
    for badix in badixs:
        originaldf.loc[badix,'quality'] = c.badqc
        logger.info('Bad data detected: ' + str(badix))
    return originaldf
