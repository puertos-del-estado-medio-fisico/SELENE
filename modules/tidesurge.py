'''
tidesurge-module
Created on 7 jun. 2018
@author: AMG
'''
import os
import logging
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
import utils.dataframe as dataframe
import utils.foreman as foreman
def tidesurge(infile,outfile,astofile,harmfile,startdate,enddate,mode,interval,stationid,stationname,latitude,longitude,originalseries,logger,config):
    #create input file for foreman prediction component
    foreman.createinputfile(infile,astofile,harmfile,startdate,enddate,mode,interval,stationid,stationname,latitude,longitude,logger)
    #run foreman
    foreman.run(infile,outfile,logger,config)
    data = []
    with open(outfile, 'r') as out:
        for ix, line in enumerate(out):
            if ix > 2:
                #3220  0.1000 28 418    3246.0    3299.4    3350.0    3397.6    3442.2    3483.6    3521.8    3556.5      0.1000
                try:
                    hourseed = float(line[6:13])
                except ValueError:
                    print(line)
                    print(line[6:13])
                    exit
                for iy,value in enumerate(np.array(line[20:].split()[:-1]).astype(np.float)):
                    dateforeman = datetime.strptime(str(int(line[14:16])).zfill(2)+str(int(line[16:18])).zfill(2)+str(int(line[18:20])).zfill(2), '%d%m%y') + timedelta(hours=hourseed+(iy*interval))
                    data.append({'date':dateforeman,'data':value,'quality':1})
    if logger.getEffectiveLevel() != logging.DEBUG:
        os.remove(infile)
        os.remove(outfile)
    predidf = pd.DataFrame(data)
    predidf = predidf.sort_values(by='date', ascending=True)
    predidf = predidf.set_index('date')
    originalinterval = dataframe.mininterval(originalseries)
    predicinterval = interval * 60
    if originalinterval == predicinterval:
        pass
    else:
        predidf = predidf.resample(str(originalinterval) + 'T').mean()
        predidf = predidf.interpolate()
    surge = originalseries - predidf
    return [surge[surge.first_valid_index():surge.last_valid_index()].round(2),predidf]
