#!/usr/bin/env python
# coding: utf-8

# getAllMutualFunds.py 
#   Get a list of all mutual funds
#   Probably only needs to run 1x per year
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 getAllMutualFunds.py              -> outputs in allMutualFunds.xlsx
#   python3 getAllMutualFunds.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1     210516      Initial Functionality

import pandas as pd
import requests

from string import ascii_lowercase
from InvestingBase import procRequest, seralizeData

# Found on StackOverflow
# percent float from 0 to 1. 
def drawProgressBar(percent, barLen = 20):
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()

# We have a table with symbols and descriptions
#   add to an existing list
def mwBuildFunds(reducedPage, fundList):
    it = iter(reducedPage)
    for symbol in it:
        description = next(it)
        fundList.append([symbol, description])

# Start with a full webpage and reduce to the table
#   Remove any remaining html tags
def mwReducePage(fullPage):
    # Start of the table
    tableLoc = fullPage.find('Fund Name') + len('Fund Name')
    fullPage = fullPage[tableLoc:]

    # End of the table
    tableLoc = fullPage.find('/table')
    fullPage = fullPage[:tableLoc]

    # Remove remaining html tags
    reducedPage = []
    for line in fullPage.splitlines(True):
        line = line.lstrip()
        if not (line.startswith('<')):
            reducedPage.append(line.rstrip('\n'))

    # Sometimes the first element in the list is blank...
    if(reducedPage[0] == ''):
        reducedPage.pop(0)

    return reducedPage

# Find the name and description of existing mutual funds
def allMutualFunds(filename):
    # String to locate funds
    URL = 'https://www.marketwatch.com/tools/mutual-fund/list/'
    
    fundList = []                               # Allocate list to hold data
    ltrCount = 1
    for letter in ascii_lowercase:
        drawProgressBar(ltrCount/len(ascii_lowercase))
        ltrCount+=1

        URLSym = URL + letter

        mwPage = procRequest(URLSym, 1, False)  # need to append a letter 'A'->'Z'
        mwPage = mwReducePage(mwPage)
        mwBuildFunds(mwPage, fundList)

    print('')
    cols = ['Symbol', 'Description']
    seralizeData(filename, fundList, cols)      # Seralize data

if __name__ == "__main__":
    import sys
    
    filename = 'allMutualFunds.xlsx'
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    allMutualFunds(filename)
