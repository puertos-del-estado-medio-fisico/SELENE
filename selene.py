'''
selene
Created on 5 jun. 2018
@author: AMG
'''
import sys
import time
import logging
import configparser
import json
import pandas as pd
import numpy as np
import configuration.constants as c
import utils.iofilehandler as iofilehandler
import utils.dataframe as dataframe
import modules.qc as qc
import modules.filterhandler as filt
import modules.tidesurge as surge
import modules.interpolation as inter
stationid = sys.argv[1]
initime = time.time()
#log
extralogatt = {'station':stationid}
logger = logging.getLogger('selene')
fh = logging.FileHandler(c.logfile)
fh.setFormatter(logging.Formatter('%(asctime)s %(station)s %(levelname)s %(message)s'))
logger.addHandler(fh) 
logger.setLevel(logging.INFO)
logger = logging.LoggerAdapter(logger, extralogatt)
#config
t = time.time()
logger.info('SELENE application >> started!')
config = configparser.ConfigParser()
config.read(c.configini)
logger.info('Config file: ' + c.configini + ' read!')
with open(c.stationsfile) as f:
    stations = json.load(f)
logger.info('Stations json file: ' + c.stationsfile + ' loaded!')
logger.debug('TIME to read config and json files: ' + str(time.time() - t) + ' seconds')
if stationid not in stations:
    logger.error('Station id ' + stationid + ' not set in stations.json. SELENE terminated!')
    sys.exit()
try:
    t = time.time()
    #ORIGINAL SAMPLING SEA LEVEL
    originaldf = iofilehandler.txtfile2dataframe(stations[stationid]['seriesfile'],stations[stationid]['seriesseparator'],list(map(int,stations[stationid]['seriesdatecolumns'].split(','))),stations[stationid]['seriesdateformat'],stations[stationid]['seriesvaluecolumn'],stations[stationid]['seriesqccolumn'],logger)
    if originaldf.empty:
        logger.info('Empty file for station ' + stationid)
        sys.exit()
    foremanstartdate = pd.to_datetime(originaldf.index.values[0])
    foremanenddate = pd.to_datetime(originaldf.index.values[-1])
    logger.debug('TIME to create dataframe from series file: ' + str(time.time() - t) + ' seconds')
    t = time.time()
    if originaldf[(originaldf.quality != 4) & (originaldf.quality != 9)].empty == True:
        logger.info('All data in station ' + stationid + ' is wrong or null (qc = 4 or qc = 9)')
        sys.exit()
    #ORIGINAL SAMPLING DATA WITH FLAGS
    originaldfwithflags = qc.qc(originaldf,stations[stationid]['qc_level_nsigma'],stations[stationid]['qc_level_winsize'],stations[stationid]['qc_level_splinedegree'],stations[stationid]['qc_stucklimit'],stations[stationid]['maxlevel'],stations[stationid]['minlevel'],logger,c)
    logger.info('TIME to check quality - qc module: ' + str(time.time() - t) + ' seconds')
    t = time.time()
    originalmininterval = dataframe.mininterval(originaldf)
    if originalmininterval <= 0:
        originalmininterval = 1
    if stations[stationid]['foremanharmfile']:
        #ORIGINAL SAMPLING INTERPOLATED DATA
        originaldfinterpolated = inter.interpolate(originaldfwithflags,None,originalmininterval,logger,config,c)
        logger.debug('TIME to interpolate to original sampling - interpolation module: ' + str(time.time() - t) + ' seconds')
        t = time.time()
        #ORIGINAL SAMPLING SURGE
        suregeresult = surge.tidesurge('foreman_min_' + stationid + '.in', 'foreman_min_' + stationid + '.out',c.foremanastofile, config['foreman']['harmonicsfolder']+stations[stationid]['foremanharmfile'],foremanstartdate,foremanenddate,c.foremanmode,c.foremanmininterval,stationid,stations[stationid]['name'],stations[stationid]['latitude'],stations[stationid]['longitude'],originaldfinterpolated,logger,config)
        tidesurgedf = suregeresult[0]
        foremanpredictionmin = suregeresult [1]
        logger.debug('TIME to calculate tide surge - tidesurge module: ' + str(time.time() - t) + ' seconds')
        t = time.time()
        #ORIGINAL SAMPLING SURGE WITH FLAGS    
        tidesurgedfnans = tidesurgedf[np.isnan(tidesurgedf.data)]  # flag nones
        if not tidesurgedfnans.empty:
            for ix in tidesurgedfnans.index.values:
                originaldfwithflags.loc[ix, 'quality'] = c.badqc
        tidesurgedfnonans = tidesurgedf.dropna(subset=['data'])  # clean none/empty values to apply quality control procedure
        tidesurgedfwithflags = qc.qc(tidesurgedfnonans,stations[stationid]['qc_surge_nsigma'],stations[stationid]['qc_surge_winsize'],stations[stationid]['qc_surge_splinedegree'],stations[stationid]['qc_stucklimit'],stations[stationid]['maxsurge'],stations[stationid]['minsurge'],logger,c)
        logger.info('TIME to check quality in surge - qc module: ' + str(time.time() - t) + ' seconds')
        t = time.time()
        #Apply flags detected in surge quality control to original series
        tidesurgebadflags = tidesurgedfwithflags[tidesurgedfwithflags.quality == c.badqc]
        if not tidesurgebadflags.empty:
            for ix in tidesurgebadflags.index.values:
                originaldfwithflags.loc[ix,'quality'] = c.badqc
        logger.debug('TIME to apply surge bad data flag to original series: ' + str(time.time() - t) + ' seconds')
        t = time.time()
    dataframe.save(originaldfwithflags.fillna('None'),config['general']['outputfolder']+stationid+'_original_sampling_flags.out')
    #5-MIN INTERPOLATED DATA
    fivemindfinterpolated = inter.interpolate(originaldfwithflags,5,originalmininterval,logger,config,c)
    logger.debug('TIME to interpolate to 5min sampling - interpolation module: ' + str(time.time() - t) + ' seconds')
    t = time.time()
    dataframe.save(fivemindfinterpolated.fillna('None'),config['general']['outputfolder']+stationid+'_5min_interpolated.out')
    #HOURLY LEVEL FILTER VALUES
    hourlyfiltered = filt.filt('pugh',fivemindfinterpolated,5,logger,config,c)
    logger.info('TIME to filter to hourly values - filterhandler module: ' + str(time.time() - t) + ' seconds')
    t = time.time()
    dataframe.save(hourlyfiltered.fillna('None'),config['general']['outputfolder']+stationid+'_hourly_slev.out')
    if stations[stationid]['foremanharmfile']:
        #HOURLY METEOROLOGICAL SURGE
        surgeresult = surge.tidesurge('foreman_hour_' + stationid + '.in', 'foreman_hour_' + stationid + '.out',c.foremanastofile,config['foreman']['harmonicsfolder']+stations[stationid]['foremanharmfile'],foremanstartdate,foremanenddate,c.foremanmode,c.foremanhourlyinterval,stationid,stations[stationid]['name'],stations[stationid]['latitude'],stations[stationid]['longitude'],hourlyfiltered,logger,config)
        hourlytidesurgedf = surgeresult[0]
        foremanpredictionhour = surgeresult[1]
        logger.debug('TIME to calculate hourly tide surge - tidesurge module: ' + str(time.time() - t) + ' seconds')
        t = time.time()
        dataframe.save(foremanpredictionhour.fillna('None'),config['general']['outputfolder']+stationid+'_hourly_prediction.out')
        dataframe.save(hourlytidesurgedf.fillna('None'),config['general']['outputfolder']+stationid+'_hourly_surge.out')
except Exception as e:
    logger.error('Error processing station: ' + stationid)
    logger.error(sys.exc_info())
logger.info('Elapsed time... ' + str(time.time() - initime) + ' seconds')
