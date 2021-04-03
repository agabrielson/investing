#!/usr/bin/env python
# coding: utf-8

# monthlyMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#
# Examples
#   python3 monthlyMetrics.py               -> outputs in interestSymbols.xlsx
#   python3 monthlyMetrics.py data.xlsx     -> outputs in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 monthlyMetrics.py march.xlsx 3
#       Notes: Collect data for March of this year, outputs in march.xlsx 
#
# Rev History:
#   0.1     210303      Initial Functionality
#   0.2     210403      Added previous month lookup
#   0.21    210403      Cleaned up code flow for one path

import yfinance as yf
import pandas as pd
from datetime import date

def getMetrics(symbol, month):
    todays_date = date.today()
    year = date.today().year
    if month is None:
        month = date.today().month - 1
        
    if isinstance(month, str):
        month = int(month)
       
    start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    end = "%4.4d-%2.2d-%2.2d" % (year, month+1, 1)
    symDaily = yf.download(symbol, start, end, interval="1m")

    #print(symDaily)
    dayFirst = symDaily.iloc[0].Close
    dayEnd = symDaily.iloc[-1].Close

    dataList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]    
    return dataList

def sortSymbols(symbols):
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    symbols = res
    return symbols

def seralizeData(filename, dataList):
    df = pd.DataFrame (dataList,columns=['Symbol', 'Month Start', 'Month End', 'PERC'])
    df = df.T
    #print(df)
    df.to_excel(filename)

def monthlyMetric(month, filename):
    # Allocate data & define symbols of interest
    dataList = []
    symbols = ['FSMEX', 'FXAIX', 'FNCMX', 'FCNTX', 'VTIVX', 'BFOCX', 'FBNDX', 'FSSNX', 'FBALX', 'FOCPX', 
                'FBGRX', 'FSLEX', 'FDLSX', 'FSLBX', 'FTRNX', 'FPURX', 'FDGRX', 'FEMKX', 'FBNDX', 'FSRPX',
                'FNBGX', 'FNORX', 'FBALX', 'FSMAX', 'FDSCX', 'AWTAX', 'FSDPX', 'FFGCX', 'FSPTX', 'FNILX',
                'FZROX', 'FSENX', 'FCPVX', 'FSHOX', 'FNARX']
    #symbols = ['FSMEX']

    # Sort symbols & remove duplicates
    symbols = sortSymbols(symbols)

    # lookup data
    for symbol in symbols:
        dataList.append(getMetrics(symbol, month))

    #Seralize data
    seralizeData(filename, dataList)

if __name__ == "__main__":
    import sys
        
    month = None
    if(len(sys.argv) >= 3):
        month = sys.argv[2]

    filename = 'interestSymbols.xlsx'
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    monthlyMetric(month, filename)
