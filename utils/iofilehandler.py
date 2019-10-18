'''
preprocess-util
Created on 17 may. 2018
@author: AMG
'''
from configuration import constants as c
from datetime import datetime as dtime 
import pandas as pd
#Examples:   
#getDataframe1(file,None,[1,2],'%Y%m%d%H%M%S',3,4)
#getDataframe2(file,',',[0],'%Y/%m/%d %H:%M',1,None)
#getDataframe3(file,None,[0,1],'%Y-%m-%d%H:%M:%S',2,3)
def txtfile2dataframe(txtfile,separator,datecolumns,datepattern,datacolumn,qualitycolumn,logger):
    data = []
    if not separator:
        separator = None
    with open(txtfile) as f:
        for line in f.readlines():
            if len(line) == 0:
                continue
            linearray = line.split(separator)
            datestring = ''
            for i in datecolumns:
                datestring = datestring + linearray[i]
            if qualitycolumn == None:
                qualityvalue = c.goodqc
            else:
                try:
                    qualityvalue = int(float(linearray[qualitycolumn]))
                    if qualityvalue == 0:
                        qualityvalue = c.goodqc
                except (IndexError, ValueError):
                    qualityvalue = c.goodqc
            try:
                datavalue = float(linearray[datacolumn])
                data.append({'date':dtime.strptime(datestring, datepattern),'data':datavalue,'quality':qualityvalue})
            except (IndexError, ValueError):
                logger.info("None or not valid value at " + datestring)
    df = pd.DataFrame(data)
    if not df.empty: 
        df = df.sort_values(by='date', ascending=True)
        df = df.set_index('date')
    return df
def filterwindow(filfile):
    window = []
    with open(filfile) as f:
        for line in f.readlines():
            linearray = line.split()
            if len(linearray)==3: #F0
                window.extend(linearray[2:3])
            if len(linearray)==8: #F1-54
                window.extend(linearray[2:8])
    return window
