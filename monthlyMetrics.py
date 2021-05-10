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
#   0.32    210425      InvestingMetrics - moved getMetrics
#   0.35    210501      Enhance symbol input

import pandas as pd
from InvestingBase import readFunds, sortSymbols, seralizeData
from InvestingMetrics import getMetrics

def monthlyMetric(filename, month, year):
    symbols = readFunds('Symbols.csv')
    #symbols = readFunds('SymbolsDebug.csv')

    sortSymbols(symbols)                # Sort symbols & remove duplicates

    dataList = []                       # Allocate variable name
    for symbol in symbols.index:        # Lookup symbols
        print(symbol)
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
