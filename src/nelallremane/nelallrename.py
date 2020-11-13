# -*- coding: utf-8 -*-
###############################################################
# Author:       patrice.ponchant@furgo.com  (Fugro Brasil)    #
# Created:      04/11/2020                                    #
# Python :      3.x                                           #
###############################################################

# The future package will provide support for running your code on Python 2.6, 2.7, and 3.3+ mostly unchanged.
# http://python-future.org/quickstart.html
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from pathlib import Path
path = Path(__file__).resolve().parents[1]

# https://github.com/pktrigg/pyall
from pyall import *

##### For the basic function #####
import datetime
import sys
import glob
import os
import subprocess

import csv
import pandas as pd
import numpy as np

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

# progress bar
from tqdm import *

# 417574686f723a205061747269636520506f6e6368616e74
####### Code #######
def main():
    parser = ArgumentParser(description='Rename the *.all files using the colunm linename inside the *.nel',
        epilog='Example: \n To rename the *.all file use python nelallremane.py c:/temp/all/ c:/temp/nel/ \n', formatter_class=RawTextHelpFormatter)
    parser.add_argument('allFolder', action='store', help='allFolder (str): ALL folder path. This is the path where the *.all files to process are.')
    parser.add_argument('nelFolder', action='store', help='nelFolder (str): NEl folder path. This is the path where the *.nel files to process are.')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    process(args)

def process(args):
    """
    Uses this if called as __main__.
    """
    allFolder = args.allFolder
    nelFolder = args.nelFolder
    
    allListFile = glob.glob(allFolder + "\\*.all")
    #nelListFile = glob.glob(nelFolder + "\\*.nel")
    nelListFile = glob.glob(nelFolder + "\\Logging\\LogSPL\\*.nel") # if Starfix SPL folder    
    
    dfNel = pd.DataFrame(columns = ["StartNel", "LineName"])
       
    print('')
    print('Reading the NEl File')
    with tqdm(total=len(nelListFile)) as pbar:
        for n in nelListFile:
            LineStart, LineName = NEL2CSV("LineRunline", n , nelFolder)
            nel_series = pd.Series([LineStart, LineName], index = dfNel.columns)
            dfNel = dfNel.append(nel_series, ignore_index=True)    
            pbar.update(1)
    
    Today = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
    dfNel["EndNel"] = dfNel.StartNel.shift(-1).replace(np.nan, Today)    
    dfNel["LineName"] = dfNel["LineName"].str.replace('"', '')
    dfNel["LineName"] = dfNel["LineName"].str.replace(' ', '')
    dfNel.StartNel = pd.to_datetime(dfNel.StartNel, format='%d/%m/%Y %H:%M:%S.%f') # format='%d/%m/%Y %H:%M:%S.%f' format='%Y/%m/%d %H:%M:%S.%f' 
    dfNel.EndNel = pd.to_datetime(dfNel.EndNel, format='%d/%m/%Y %H:%M:%S.%f')
    
    dfAll = pd.DataFrame(columns = ["AllPath", "StartAll", "EndAll"]) 
            
    print('')
    print('Reading the ALL File')
    with tqdm(total=len(allListFile)) as pbar:
        for f in allListFile:
            # reading ALL file (count, start, end)
            r = ALLReader(f)            
            count, StartAll, EndAll = r.getRecordCount() # read through the entire file as fast as possible to get a count of all records.
            all_series = pd.Series([f, StartAll, EndAll], index = dfAll.columns)
            dfAll = dfAll.append(all_series, ignore_index=True)        
            r.rewind()
            r.close()                     
            pbar.update(1)
    
    dfAll.StartAll = pd.to_datetime(dfAll.StartAll, unit='s')  # format='%d/%m/%Y %H:%M:%S.%f' format='%Y/%m/%d %H:%M:%S.%f'
    dfAll.EndAll = pd.to_datetime(dfAll.EndAll, unit='s')
    dfLog = pd.DataFrame(columns = ["AllStartTime", "AllEndTime", "File Path", "File Name", "Linename", "New File Name"])
           
    print('')
    print('Renaming the ALL files')
    with tqdm(total=len(allListFile)) as pbar:
        for index, row in dfNel.iterrows():                  
            Start = row['StartNel']
            End = row['EndNel']
            Name = row['LineName']   
            dffilter = dfAll[dfAll.StartAll.between(Start, End)]   
            for index, el in dffilter.iterrows():
                AllFile =  el['AllPath']
                AllStartTime = el['StartAll']
                AllEndTime = el['EndAll']          
                FolderName = os.path.split(AllFile)[0]
                ALLName = os.path.splitext(os.path.basename(AllFile))[0]                               
                NewName = FolderName + '\\' + ALLName + '_' + Name + '.all'
                dfLog = dfLog.append(pd.Series([AllStartTime, AllEndTime, FolderName, ALLName, Name, NewName], 
                                       index=dfLog.columns ), ignore_index=True)                
                if os.path.isfile(AllFile):
                    os.rename(AllFile, NewName)        
                pbar.update(1)
    dfLog.to_csv(allFolder + "MBES_Logs.csv", index=False)

##### Convert NEL to CSV #####
def NEL2CSV(Nelkey, NelFileName, Path):
    FileName = os.path.splitext(os.path.basename(NelFileName))[0]    
    csvfilepath = Path + FileName + "_" + Nelkey + '.csv'
    cmd = 'for %i in ("' + NelFileName + '") do nel2asc -v "%i" ' + Nelkey + ' > ' + csvfilepath
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    dfS = pd.read_csv(csvfilepath, header=None)
    LineStart = dfS.iloc[0][0]
    LineName = dfS.iloc[0][3]   
        
    os.remove(csvfilepath)   
    
    return LineStart, LineName


if __name__ == "__main__":
    now = datetime.datetime.now() # time the process
    main()
    print('')
    print("Process Duration: ", (datetime.datetime.now() - now)) # print the processing time. It is handy to keep an eye on processing performance.