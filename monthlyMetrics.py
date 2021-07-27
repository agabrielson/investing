#!/usr/bin/env python
# coding: utf-8

# monthlyMetrics.py
#
# Inputs
#   investType: Investment type -> fund or ETF
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#   year:       year to collect data points for, can be left blank
#
# Examples
#   python3 monthlyMetrics.py               -> outputs funds data in fundMonthly.xlsx
#   python3 monthlyMetrics.py etf           -> outputs etf data in etfMonthly.xlsx
#   python3 monthlyMetrics.py fund data.xlsx-> outputs fund data in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 monthlyMetrics.py etf march.xlsx 3
#       Notes: Collect data for March of this year, outputs in march.xlsx 
#   python3 monthlyMetrics.py fund dec2020fund.xlsx 12 2020
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
#   0.4     210726      Switch between funds & ETFs

import pandas as pd
from InvestingBase import readFunds, sortSymbols, seralizeData
from InvestingMetrics import getMetrics

def monthlyMetric(investType, filename, month, year):
    # Get symbols of interest & sort -> Update Fund vs ETF
    if(investType.lower().strip() == 'fund'):
        symbols = readFunds('Symbols.csv')
        #symbols = readFunds('SymbolsDebug.csv')
    elif(investType.lower().strip() == 'etf'):
        symbols = readFunds('SymbolsETF.csv')
        #symbols = readFunds('SymbolsETFDebug.csv')
    else:
        print('Type should be fund or etf')
        return

    sortSymbols(symbols)                # Sort symbols & remove duplicates

    dataList = []                       # Allocate variable name
    for symbol in symbols.index:        # Lookup symbols
        symbol = symbol.strip()
        print(symbol)
        dataList.append(getMetrics(symbol, month, year))

    cols = ['Symbol', 'Month Start', 'Month End', 'PERC']
    seralizeData(filename, dataList, cols)    # Seralize data

if __name__ == "__main__":
    import sys
    
    investType = 'fund'
    if(len(sys.argv) >= 2):
        investType = sys.argv[1]

    filename = 'etfMonthly.xlsx'       # File name to seralize data
    if(investType == 'fund'):
        filename = 'fundMonthly.xlsx'

    if(len(sys.argv) >= 3):
        filename = sys.argv[2]

    month = None                        # month to lookup
    if(len(sys.argv) >= 4):
        month = sys.argv[3]

    year = None                        # month to lookup
    if(len(sys.argv) >= 5):
        year = sys.argv[4]

    monthlyMetric(investType, filename, month, year)      # run monthMetrics to collect data
