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
#   python3 monthlyMetrics.py dec2020.xlsx 12 2020
#
# Rev History:
#   0.1     210303      Initial Functionality
#   0.2     210403      Added previous month lookup
#   0.21    210403      Cleaned up code flow for one path
#   0.25    210405      Added year

import yfinance as yf
import pandas as pd
from datetime import date

def startMonthYear(month, year):
    if year is None:
        year = date.today().year

    if isinstance(year, str):
        year = int(year)

    if month is None:
        month = date.today().month - 1
        
    if isinstance(month, str):
        month = int(month)
    
    return month, year;

def endMonthYear(month, year):
    month, year = startMonthYear(month, year)
    month = month + 1
    if month == 13:
        month = 1
        year = year + 1

    return month, year;

def getMetrics(symbol, month, year):
    month, year = startMonthYear(month, year)
    monthEnd, yearEnd = endMonthYear(month, year)

    start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    end = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)
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

def monthlyMetric(filename, month, year):
    # Define symbols of interest
    symbols = ['FSMEX', 'FXAIX', 'FNCMX', 'FCNTX', 'VTIVX', 'BFOCX', 'FBNDX', 'FSSNX', 'FBALX', 'FOCPX', 
                'FBGRX', 'FSLEX', 'FDLSX', 'FSLBX', 'FTRNX', 'FPURX', 'FDGRX', 'FEMKX', 'FBNDX', 'FSRPX',
                'FNBGX', 'FNORX', 'FBALX', 'FSMAX', 'FDSCX', 'AWTAX', 'FSDPX', 'FFGCX', 'FSPTX', 'FNILX',
                'FZROX', 'FSENX', 'FCPVX', 'FSHOX', 'FNARX']
    #symbols = ['FSMEX']

    symbols = sortSymbols(symbols)      # Sort symbols & remove duplicates

    dataList = []                       # Allocate variable name
    for symbol in symbols:              # Lookup symbols
        dataList.append(getMetrics(symbol, month, year))
    
    seralizeData(filename, dataList)    # Seralize data

if __name__ == "__main__":
    import sys
    
    year = None                        # month to lookup
    if(len(sys.argv) >= 4):
        year = sys.argv[3]

    month = None                        # month to lookup
    if(len(sys.argv) >= 3):
        month = sys.argv[2]

    filename = 'interestSymbols.xlsx'   # File name to seralize data
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    monthlyMetric(filename, month, year)      # run monthMetrics to collect data
