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
    parser = ArgumentParser(description='Rename the *.all files using the *-position.fbf or .fbz files',
        epilog='Example: \n To rename the *.all file use python splallremane.py -r -fbz c:/temp/all/ c:/temp/fbf/ FugroBrasilis-CRP-Position \n',
        formatter_class=RawTextHelpFormatter)    
    parser.add_argument('-r', action='store_true', default=False, dest='recursive', help='Search recursively for XTF files.')
    parser.add_argument('-fbz', action='store_true', default=False, dest='fbfFormat', help='If FBZ, use this argument.')
    parser.add_argument('allFolder', action='store', help='allFolder (str): ALL folder path. This is the path where the *.all files to process are.')
    parser.add_argument('splFolder', action='store', help='splFolder (str): SPL folder path. This is the path where the *.fbf/*.fbz files to process are.')
    parser.add_argument('SPLposition', action='store', help='SPLposition (str): SPL postion file to be use to rename the *.all.')
    
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
    splFolder = args.splFolder
    SPLposition = args.SPLposition
    
    # Defined Dataframe
    dfSPL = pd.DataFrame(columns = ["SessionStart", "SessionEnd", "LineName"])
    #dfAll = pd.DataFrame(columns = ["AllPath", "AllStartTime", "AllEndTime"])
    dfAll = pd.DataFrame(columns = ["AllStartTime", "AllEndTime", "FilePath", "FileName", "Linename", "NewFileName"]) 
    dftmp = pd.DataFrame(columns = ["AllStartTime", "AllEndTime", "FilePath", "FileName", "Linename", "NewFileName"]) 
    
    # Check if SPL is a position file   
    if SPLposition.find('-Position') == -1:
        print ("The SPL file %s is not a position file, quitting" % SPLposition)
        exit()
    
    if args.recursive:
        allListFile = glob.glob(allFolder + "\\**\\*.all", recursive=True)
    else:
        allListFile = glob.glob(allFolder + "\\*.all")
        
    if args.fbfFormat:
        splListFile = glob.glob(splFolder + "\\**\\" + SPLposition + ".fbz", recursive=True)
    else:
        splListFile = glob.glob(splFolder + "\\**\\" + SPLposition + ".fbf", recursive=True)
        print('')
        print('Reading the FBF Files')
        with tqdm(total=len(splListFile)) as pbar:
            for n in splListFile:
                SessionStart, SessionEnd, LineName = FBF2CSV(n , splFolder)
                dfSPL = dfSPL.append(pd.Series([SessionStart, SessionEnd, LineName], 
                                       index=dfSPL.columns ), ignore_index=True)           
                pbar.update(1)
        

    # Format datetime
    dfSPL.SessionStart = pd.to_datetime(dfSPL.SessionStart, format='%d/%m/%Y %H:%M:%S.%f') # format='%d/%m/%Y %H:%M:%S.%f' format='%Y/%m/%d %H:%M:%S.%f' 
    dfSPL.SessionEnd = pd.to_datetime(dfSPL.SessionEnd, format='%d/%m/%Y %H:%M:%S.%f')
           
    print('')
    print('Reading the ALL File')
    with tqdm(total=len(allListFile)) as pbar:
        for f in allListFile:
            # reading ALL file (count, start, end)
            r = ALLReader(f)            
            count, AllStartTime, AllEndTime = r.getRecordCount() # read through the entire file as fast as possible to get a count of all records.
            ALLName = os.path.splitext(os.path.basename(f))[0] 
            dfAll = dfAll.append(pd.Series([AllStartTime, AllEndTime, f, ALLName, "", ""], 
                        index=dfAll.columns ), ignore_index=True)    
            r.rewind()
            r.close()                     
            pbar.update(1)

    # Format datetime
    dfAll.AllStartTime = pd.to_datetime(dfAll.AllStartTime, unit='s')  # format='%d/%m/%Y %H:%M:%S.%f' format='%Y/%m/%d %H:%M:%S.%f'
    dfAll.AllEndTime = pd.to_datetime(dfAll.AllEndTime, unit='s')
        
    print('')
    print('Renaming the ALL files')
    with tqdm(total=len(allListFile)) as pbar:
        for index, row in dfSPL.iterrows():                  
            Start = row['SessionStart']
            End = row['SessionEnd']
            Name = row['LineName']   
            dffilter = dfAll[dfAll.AllStartTime.between(Start, End)]
            for index, el in dffilter.iterrows():
                AllFile =  el['FilePath']
                AllStartTime = el['AllStartTime']
                AllEndTime = el['AllEndTime']          
                FolderName = os.path.split(AllFile)[0]
                ALLName = os.path.splitext(os.path.basename(AllFile))[0]                               
                NewName = FolderName + '\\' + ALLName + '_' + Name + '.all'
                dftmp = dftmp.append(pd.Series([AllStartTime, AllEndTime, AllFile, ALLName, Name, NewName], 
                                    index=dftmp.columns ), ignore_index=True)                
                if os.path.isfile(AllFile):
                    os.rename(AllFile, NewName)        
                pbar.update(1)
                
    # Updated the final dataframe to export the log
    dfAll.set_index('AllStartTime', inplace=True)
    dftmp.set_index('AllStartTime', inplace=True)
    dfAll.update(dftmp)
    dfAll.to_csv(allFolder + "MBES_Logs.csv", index=True)

##### Convert NEL/FBF/FBZ to CSV #####
def NEL2CSV(Nelkey, NelFileName, Path):
    ##### Convert NEL to CSV #####
    FileName = os.path.splitext(os.path.basename(NelFileName))[0]    
    csvfilepath = Path + FileName + "_" + Nelkey + '.csv'
    cmd = 'for %i in ("' + NelFileName + '") do nel2asc -v "%i" ' + Nelkey + ' > ' + csvfilepath
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    #created the variables
    dfS = pd.read_csv(csvfilepath, header=None, skipinitialspace=True)
    LineStart = dfS.iloc[0][0]
    LineName = dfS.iloc[0][3]
    
    #cleaning
    os.remove(csvfilepath)
    del dfS, FileName, csvfilepath   
    
    return LineStart, LineName

def FBF2CSV(FBFFileName, Path):
    ##### Convert FBF to CSV #####
    FileName = os.path.splitext(os.path.basename(FBFFileName))[0]    
    fbffilepath = Path + FileName + '.csv'
    cmd = 'for %i in ("' + FBFFileName + '") do fbf2asc -i %i -o "' + fbffilepath + '"'
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    #subprocess.call(cmd, shell=True) ### For debugging
    
    #created the variables
    dfS = pd.read_csv(fbffilepath, header=None, skipinitialspace=True, na_values='NoLineName')

    SessionStart = dfS.iloc[0][0]
    SessionEnd = dfS.iloc[-1][0]
    LineName = dfS.iloc[0][8]
    
    #cleaning  
    os.remove(fbffilepath)
    del dfS, FileName, fbffilepath
    
    #checking if linename is empty as is use in all other process
    if pd.isnull(LineName):
        print ("Linename is empty in %s, quitting" % FBFFileName)
        exit()
    else:
        return SessionStart, SessionEnd, LineName   

def FBZ2CSV(FBZFileName, Path):
    ##### Convert FBZ to CSV #####
    FileName = os.path.splitext(os.path.basename(FBZFileName))[0]    
    fbzfilepath = Path + FileName + '.csv'
    cmd = 'for %i in ("' + FBZFileName + '") do C:\ProgramData\Fugro\Starfix2018\Fugro.DescribedData2Ascii.exe %i > "' + fbzfilepath + '"'
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    #subprocess.call(cmd, shell=True) ### For debugging
    
    #created the variables
    dfS = pd.read_csv(fbzfilepath, header=None, skipinitialspace=True, na_values='NoLineName')

    SessionStart = dfS.iloc[0][0]
    SessionEnd = dfS.iloc[-1][0]
    LineName = dfS.iloc[0][8]
    
    #cleaning  
    os.remove(fbzfilepath)
    del dfS, FileName, fbzfilepath
    
    #checking if linename is empty as is use in all other process
    if pd.isnull(LineName):
        print ("Linename is empty in %s, quitting" % FBZFileName)
        exit()
    else:
        return SessionStart, SessionEnd, LineName

  
if __name__ == "__main__":
    now = datetime.datetime.now() # time the process
    main()
    print('')
    print("Process Duration: ", (datetime.datetime.now() - now)) # print the processing time. It is handy to keep an eye on processing performance.