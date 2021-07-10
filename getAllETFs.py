#!/usr/bin/env python
# coding: utf-8

# getAllETFs.py 
#   Get a list of all ETFs
#   Probably only needs to run 1x per year
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 getAllETFs.py              -> outputs in allETFs.xlsx
#   python3 getAllETFs.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1     210710      Initial Functionality
#   0.15    210710      Get all ETFs, not just first page of each letter

import pandas as pd
import requests
import re

from string import ascii_lowercase
from InvestingBase import procRequest, seralizeData

# Found on StackOverflow
# percent float from 0 to 1. 
def drawProgressBar(percent, barLen = 20):
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()

def stripHTML(entry):
    # Remove remaining html tags
    strippedEntry = []
    if type(entry) is not str: 
        print(entry)
        entry = ' '.join([str(elem) for elem in entry])

    for line in entry.splitlines(True):
        line = line.lstrip()
        if not (line.startswith('<')):
            strippedEntry.append(line.rstrip('\n'))

    strippedEntry[1] = strippedEntry[1][1:-1]
    
    print(strippedEntry[1])

    return strippedEntry


# We have a table with symbols and descriptions
#   add to an existing list
def mwBuildFunds(reducedPage, fundList):
    entry = ""
    for line in reducedPage.splitlines(True):
        if '<tr>' in line:
            entry = ""
        elif '</tr>' in line:
            entry = stripHTML(entry)
            entry[0] = entry[0].replace('amp;','')
            fundList.append(entry[0:5])
        else:
            entry += line
    
    return fundList

# Start with a full webpage and reduce to the table
#   Remove any remaining html tags
def mwReducePage(fullPage):
    # Start of the table
    tableLoc = fullPage.find('table table-condensed')
    fullPage = fullPage[tableLoc:]

    tableLoc = fullPage.find('Sector') + len('Sector')
    fullPage = fullPage[tableLoc:]

    tableLoc = fullPage.find('</tr>') + len('</tr>')
    fullPage = fullPage[tableLoc:]

    # End of the table
    tableLoc = fullPage.find('/table')
    fullPage = fullPage[:tableLoc]

    # Pages are broken up, verify there is actual data to get
    entries = fullPage.lower().split().count('</tr>')
    if(entries == 0):
        fullPage = None

    return fullPage

def getETFListings(letter, URL, fundList):
    mwPage = 'init'
    numCount = 1
    while mwPage is not None:
        # Website splits table up over many pages...
        URLSym = URL + letter + '/' + str(numCount)

        mwPage = procRequest(URLSym, 1, False)  # need to append a letter 'A'->'Z'
        mwPage = mwReducePage(mwPage)
        if mwPage is None:
            break;

        mwBuildFunds(mwPage, fundList)
        numCount+=1

    return fundList

# Find the name and description of existing mutual funds
def allMutualFunds(filename):
    # String to locate funds
    # Examples, 0-9, A-> empty, B -> B, ...
    URL = 'https://www.marketwatch.com/tools/markets/exchange-traded-funds/a-z/'
    
    fundList = []                               # Allocate list to hold data
    ltrCount = 1
    for letter in ascii_lowercase:
        drawProgressBar(ltrCount/(len(ascii_lowercase)+1))
        ltrCount+= 1
        fundList = getETFListings(letter, URL, fundList)
        
    # Do 0-9 now...
    drawProgressBar(ltrCount+1/(len(ascii_lowercase)+1))
    fundList = getETFListings('0-9', URL, fundList)

    cols = ['Name', 'Symbol', 'Country', 'Exchange', 'Sector'] # need more
    seralizeData(filename, fundList, cols)      # Seralize data
    #seralizeData(filename, fundList)

if __name__ == "__main__":
    import sys
    
    filename = 'allETFs.xlsx'
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    allMutualFunds(filename)
