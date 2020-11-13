# Rename the .all files using the *.fbf or *.fbz

## Introduction

This python script will remane the .all and create a log based on the *-Positionfbf or *-.fbz file.

## Setup

Several modules need to be install before using the script. You will need:

+ `$ pushd somepath\nelallremane`
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

* Rename the *.all files
* CSV file with all information needed to QC

## TO DO:

