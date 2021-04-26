#!/usr/bin/env python
# coding: utf-8

# monthlyMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#   year:       year to collect data points for, can be left blank
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
#   0.26    210410      Adding significantly more symbols
#   0.3     210418      Cleaning up code significantly
#   0.31    210425      Cleaning up display

import yfinance as yf

from interestingFunds import interestingFunds
from InvestingBase import startMonthYear, endMonthYear, sortSymbols, seralizeData

def getMetrics(symbol, month, year):
    month, year = startMonthYear(month, year)
    monthEnd, yearEnd = endMonthYear(month, year)

    start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    end = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)
    print(symbol)
    symDaily = yf.download(symbol, start, end, interval="1m",progress=False)

    #print(symDaily)
    dayFirst = symDaily.iloc[0].Close
    dayEnd = symDaily.iloc[-1].Close

    dataList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]    
    return dataList

def monthlyMetric(filename, month, year):
    symbols = interestingFunds()        # Get symbols of interest
    #symbols = ['FSMEX']
    
    symbols = sortSymbols(symbols)      # Sort symbols & remove duplicates

    dataList = []                       # Allocate variable name
    for symbol in symbols:              # Lookup symbols
        try:
            dataList.append(getMetrics(symbol, month, year))
        except:
            dataList.append([symbol])

    cols = ['Symbol', 'Month Start', 'Month End', 'PERC']
    seralizeData(filename, dataList, cols)    # Seralize data

if __name__ == "__main__":
    import sys
    
    year = None                        # month to lookup
    if(len(sys.argv) >= 4):
        year = sys.argv[3]

    month = None                        # month to lookup
    if(len(sys.argv) >= 3):
        month = sys.argv[2]

    filename = 'monthlySymbols.xlsx'   # File name to seralize data
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    monthlyMetric(filename, month, year)      # run monthMetrics to collect data
