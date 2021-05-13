#!/usr/bin/env python
# coding: utf-8

# stocksQuartely.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 stocksQuartely.py              -> outputs in quarterlySymbols.xlsx
#   python3 stocksQuartely.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1     210512      Initial Functionality

import yfinance as yf
import pandas as pd
import itertools 
from datetime import date
from InvestingBase import procStocks, extractTicker, seralizeData

def checkRtnVals(value):
    if(value is not None):
        return value

    return " "

def yfGetQuarterlyStock(symbol):
    sym = yf.Ticker(symbol)
    
    dateToday = date.today().strftime('%Y-%m-%d')

    sName = sym.info['symbol']
    lName = checkRtnVals(sym.info['longName'])
    
    pe = checkRtnVals(sym.info['forwardPE'])  # price to earnings
    ps = checkRtnVals(sym.info['forwardEps']) # Earnings Per Share
    beta = checkRtnVals(sym.info['beta']) # 
    divYield = checkRtnVals(sym.info['trailingAnnualDividendYield']) # Divend per share
    payout = checkRtnVals(sym.info['payoutRatio']) # % earnings paid out as dividends

    
    yfDataList = [dateToday, sName, lName, pe, ps, beta, divYield, payout]
    yfDataHdr = ['Date', 'Symbol', 'Name', 'PE', 'EPS', 'beta', 'Dividend Yield', 'payoutRatio']

    return yfDataList, yfDataHdr

# Lookup quartely metrics
#   No one source has everything
#   Some of the yahoo data appears to be suspect
#   Going to pull suspect and missing data points from MarketWatch
#   Then merge the two data sources
def getQuarterlyStock(filename):
    # SEC hosts JSON file with every ticker in the US
    URLSym = 'https://www.sec.gov/files/company_tickers.json'
    stocksJson = procStocks(URLSym)     # Obtain all tickers in JSON

    symList = extractTicker(stocksJson) # We just need the ticker symbol for this script
    #symList = ['TSLA', 'FB', 'YUM']

    dataList = []           # Allocate list to hold data
    hdrList = []            # Allocate list to hold header

    dateToday = date.today().strftime('%Y-%m-%d')
    
    for symbol in symList:  # lookup data
        print(symbol)
        try:
            symList, hdrList = yfGetQuarterlyStock(symbol)

            dataList.append(symList)
        except:
            dataList.append([dateToday, symbol])

    #Seralize data
    seralizeData(filename, dataList, hdrList)    # Seralize data

if __name__ == "__main__":
    import sys
    filename = 'quarterlyStocks.xlsx'
    if(len(sys.argv) == 2):
        filename = sys.argv[1]

    getQuarterlyStock(filename)
