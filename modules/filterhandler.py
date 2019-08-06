'''
filter-module
Created on 5 jun. 2018
@author: AMG
'''
import modules.filterkaiser as filterkaiser
import modules.filterpugh as filterpugh
def filt(filtername,df,minsampling,logger,config,c):
    if filtername == 'kaiser':
        return filterkaiser.filt(df,minsampling,logger,config)
    elif filtername == 'pugh':
        return filterpugh.filt(df,logger,c)
    else:
        logger.error('Filter option ' + filtername + ' not available.')