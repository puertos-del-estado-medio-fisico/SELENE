'''
filterhandler-module
Created on 23 may. 2018
@author: AMG
'''
from scipy.signal import kaiserord, firwin, lfilter
def filt(df,minsampling,logger,config):
    logger.info('Filter - kaiser filterhandler >> started!')
    #properties
    samplerate = 1.0 / minsampling * 60.0   #sample rate in Hz
    cutoff = float(config['filterhandler']['cutoff'])  #cutoff frequency of the filterhandler in Hz
    #Lowpass FIR filterhandler with a Kaiser window
    nyq_rate = samplerate / minsampling #nyquist rate of the signal
    width = 2.0/nyq_rate #width of the transition from pass to stop, relative to the Nyquist rate
    ripple_db = 70.0 #attenuation in the stop band in dB
    N, beta = kaiserord(ripple_db, width) #order and Kaiser parameter for the FIR filterhandler
    logger.debug('Calculated order for filterhandler = ' + str(type(N)) + ' ' + str(N))
    logger.debug('Calculated kaiser parameter beta = ' + str(type(beta)) + ' ' + str(beta))
    taps = firwin(N, cutoff/nyq_rate, window=('kaiser', beta))
    df['data'] = lfilter(taps, 1.0, df['data'])
    return df.resample('1H').first()