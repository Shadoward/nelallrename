# Rename the .all files using the *.fbf or *.fbz

## Introduction

This python script will remane the .all and create a log based on the *-Position.fbf or *-.fbz file.

## Setup

Several modules need to be install before using the script. You will need:

+ `$ pushd somepath\splallremane`
+ `$ pip install .`

## Usage

```
usage: splallrename.py [-h] [-r] [-fbz] allFolder splFolder SPLposition

Rename the *.all files using the *-position.fbf or .fbz files

positional arguments:
  allFolder    allFolder (str): ALL folder path. This is the path where the *.all files to process are.
  splFolder    splFolder (str): SPL folder path. This is the path where the *.fbf/*.fbz files to process are.
  SPLposition  SPLposition (str): SPL postion file to be use to rename the *.all.

optional arguments:
  -h, --help   show this help message and exit
  -r           Search recursively for XTF files.
  -fbz         If FBZ, use this argument.

Example:
 To rename the *.all file use python splallremane.py -r -fbz c:/temp/all/ c:/temp/fbf/ FugroBrasilis-CRP-Position
```

## Export products

+ Rename the *.all files
+ CSV logs files with all information needed to QC the data
  + Duplicate_MBES_Log.csv (MBES duplicated data)
  + NoLineNameFound_log.csv (SPL Session that do not have LineName information)
  + Full_MBES_Log.csv (Full logged data)
  + LineName_MBES_Log.csv (Log used to compare the LineName between sensor)

## TO DO
