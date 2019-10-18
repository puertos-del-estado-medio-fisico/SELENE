'''
selene
Created on 9 jun. 2018
@author: AMG
'''
import sys
import configparser
import utils.visualize as visualize
import utils.iofilehandler as iofilehandler
import json
import configuration.constants as c
import logging
#log
logger = logging.getLogger('selenevis')
fh = logging.FileHandler(c.logfilevis)
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(fh)
logger.setLevel(logging.INFO)
#config
config = configparser.ConfigParser()
config.read(c.configini)
option = sys.argv[1]
with open(c.stationsfile) as f:
    stations = json.load(f)
if option == "-station":
    station = sys.argv[2]
    dfs = []
    df = iofilehandler.txtfile2dataframe(config['general']['outputfolder']+station+'_original_sampling_flags.out', None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, 3, logger)
    dfs.append([df[df.quality != c.badqc][['data']],'Orig. sampling SLEV : OK', '#2980b9',311,1.2,'o','None', 0, 0.05, 0.5])
    dfs.append([df[df.quality == c.badqc][['data']],'Orig. sampling SLEV : BAD','#e71111',311,2.5,'o','None', 0, 0.05, 0.5])
    df = iofilehandler.txtfile2dataframe(config['general']['outputfolder']+station+'_5min_interpolated.out', None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, None, logger)
    dfs.append([df[['data']],'5-min interpolation','#2980b9',312,1.2,'o','solid', 0, 0.05, 0.5])
    df = iofilehandler.txtfile2dataframe(config['general']['outputfolder']+station+'_hourly_slev.out', None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, None, logger)
    dfs.append([df[['data']],'Hourly SLEV','#FA8072',312,3.5,'o','solid', 0, 0.05, 0.5])
    df = iofilehandler.txtfile2dataframe(config['general']['outputfolder']+station+'_hourly_surge.out', None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, None, logger)
    dfs.append([df[['data']],'Hourly Surge','#229954',313,1.8,'o','None', 0, 2, 0.5])
    visualize.plotsubplots(dfs,stations[station]['name'])
elif option == "-files":
    files = sys.argv[2].split(',')
    dfs = []
    for file in files:
        try:
            df = iofilehandler.txtfile2dataframe(file, None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, 3, logger)
            dfs.append([df[df.quality != c.badqc][['data']],file+':OK','#2274a5',1.5,'o','None'])
            dfs.append([df[df.quality == c.badqc][['data']],file+':BAD','#e71111',2.5,'o','None'])
        except IndexError:
            df = iofilehandler.txtfile2dataframe(file, None, [0,1], "\"%Y-%m-%d%H:%M:%S\"", 2, None, logger)
            dfs.append([df[['data']],file,'#2274a5',1.5,'o','None'])
    visualize.plot(dfs,sys.argv[2])
else:
    print("Unknown option. Please, use -station <stationid> or -files <file1,file2,file3>")

