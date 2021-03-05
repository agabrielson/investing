#!/usr/bin/env python
# coding: utf-8

# quartelyMetrics.py
#
# Notes: Run on the first business day of the month
#
# Rev History:
#   0.1 - 210303
#           Initial Functionality

import yfinance as yf
import pandas as pd

def getMetrics(symbol):
        newtime_daily = yf.download(symbol, period = "1mo")
        dayFirst = newtime_daily.iloc[0].Close
        dayEnd = newtime_daily.iloc[-1].Close
        
        dataList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]    
        return dataList


def monthlyMetric(filename):
    # Allocate data & define symbols of interest
    dataList = []
    symbols = ['FSMEX', 'FXAIX', 'FNCMX', 'FCNTX', 'VTIVX', 'BFOCX', 'FBNDX', 'FSSNX', 'FBALX', 'FOCPX', 
                     'FBGRX', 'FSLEX', 'FDLSX', 'FSLBX', 'FTRNX', 'FPURX', 'FDGRX', 'FEMKX', 'FBNDX', 'FSRPX',
                     'FNBGX', 'FNORX', 'FBALX', 'FSMAX', 'FDSCX', 'AWTAX', 'FSDPX', 'FFGCX', 'FSPTX', 'FNILX',
                     'FZROX' ]

    # Sort symbols & remove duplicates
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    symbols = res

    # lookup data
    for symbol in symbols:
        dataList.append(getMetrics(symbol))

    #Seralize data
    df = pd.DataFrame (dataList,columns=['Symbol', 'Month Start', 'Month End', 'PERC'])
    df = df.T
    #print(df)
    df.to_excel(filename)

if __name__ == "__main__":
        import sys
        filename = 'interestSymbols.xlsx'
        if(len(sys.argv) == 2):
            filename = sys.argv[1]

        monthlyMetric(filename)
