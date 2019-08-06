'''
foreman-util
Created on 26 may. 2018
@author: AMG
'''
import os
import configuration.constants as c
def predinfo(startdate,enddate,mode,interval):
    result = str(startdate.day).zfill(3) + str(startdate.month).zfill(3) + str(startdate.year % 1000).zfill(3) + \
    ' ' + str(enddate.day).zfill(3) + str(enddate.month).zfill(3) + str(enddate.year % 1000).zfill(3) + \
    ' ' + mode + '  ' + str(interval) + \
    '      ' + str(startdate.year)[:2].zfill(3) + str(enddate.year)[:2].zfill(3)
    return result 
def harmheader(idstation,name,latitude,longitude):
    result = '     ' + str(idstation) + ' ' + str(name) + '                ' + c.meansolartime + \
    ' ' + str(int(latitude)).zfill(2) + ' ' + str(round((abs(latitude) - abs(int(latitude))) * 60)).zfill(2) + \
    '  ' + str(int(longitude)).zfill(3) + ' ' + str(round((abs(longitude) - abs(int(longitude))) * 60)).zfill(2)
    return result
def createinputfile(targetfile,astofile,harmfile,startdate,enddate,mode,interval,idstation,name,latitude,longitude,logger):
    logger.info('Foreman - create input file >> started!')
    if os.path.isfile(targetfile):
        open(targetfile, 'w').close()   
    with open(targetfile, 'ab') as target:
        with open(astofile, 'rb') as asto:
            target.write(asto.read())
        with open(harmfile, 'rb') as harm:
            for ix, harmline in enumerate(harm):
                if ix == 0:
                    #     3217 Ferro2                MST 43 29  008 15
                    if len(name) > 6:
                        name = name[0:6]
                    target.write(harmheader(idstation,name,latitude,longitude).encode('UTF8'))
                    target.write(b"\n")
                if ix > 7:
                    target.write(harmline)
        #003010017 003011017 EQUI  0.1      020020
        target.write(predinfo(startdate,enddate,mode,interval).encode('UTF8'))          
        target.write(b" \n")
        target.write(b" \n")
        target.write(b" \n") 
def run(infile,outfile,logger,config):
    logger.info('Foreman - run prediction >> started!')
    cmd =  config['foreman']['program'] + ' ' + infile + ' ' + outfile
    failure = os.system(cmd)
    if failure:
        logger.error('Execution of "%s" failed!' % cmd)
