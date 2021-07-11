#!/usr/bin/env python
# coding: utf-8

# quartelyETFMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 quartelyETFMetrics.py              -> outputs in quarterlyETFSymbols.xlsx
#   python3 quartelyETFMetrics.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1     210711      Initial Functionality

import yfinance as yf
import pandas as pd
import itertools 
from datetime import date
from InvestingBase import readFunds, procRequest, getDate, sortSymbols, seralizeData

def mwProcData(fullPage, searchStr):
    tableLoc = fullPage.find(searchStr)
    redPage = fullPage[tableLoc:]
    reduced = redPage.splitlines()

    if (len(reduced) == 1):
        return None

    return reduced[1]

def mwGetKeyData(fullPage): 
    tableLoc = fullPage.find('Key Data')
    yrRangeVal = mwProcData(fullPage[tableLoc:], '52 Week Range')
    totAssetVal = mwProcData(fullPage[tableLoc:], 'Total Net Assets') 
    yieldVal = mwProcData(fullPage[tableLoc:], 'Yield')
    expenseRatioVal = mwProcData(fullPage[tableLoc:], 'Net Expense Ratio')
    turnoverVal = mwProcData(fullPage[tableLoc:], 'Turnover %')
    div = mwProcData(fullPage[tableLoc:], 'Dividend')
    divDate = mwProcData(fullPage[tableLoc:], 'Ex-Dividend Date')

    mwKeyDataList = [yrRangeVal, totAssetVal, yieldVal, expenseRatioVal, turnoverVal, div, divDate]
    mwKeyDataHdr = ['52 Week Range', 'Total Net Assets', 'Yield', 'Net Expense Ratio', 'Turnover %', 'Dividend', 'Ex-Dividend Date']

    return mwKeyDataList, mwKeyDataHdr

def yfGetQuarterlyMetrics(symbol):
    sym = yf.Ticker(symbol)
    
    sName = sym.info['symbol']
    lName = sym.info['longName']
    
    sustain = '-'
    if(sym.sustainability is not None):
        sustain = sym.sustainability['Value'].to_dict()['peerGroup']

    totAssets = sym.info['totalAssets']
    yieldVal = sym.info['yield']
    trailYield = sym.info['trailingAnnualDividendYield']
    threeYrRtn = sym.info['threeYearAverageReturn']
    fiveYrRtn = sym.info['fiveYearAverageReturn']

    yfDataList = [sName, lName, sustain, totAssets, yieldVal, trailYield, threeYrRtn, fiveYrRtn]
    yfDataHdr = ['Symbol', 'Name', 'Peer Group', 'Total Assets', 'yield', 'Trailing Annual Dividend Yield', '3 yr Rtn', '5 yr Rtn']

    return yfDataList, yfDataHdr

# Lookup quartely metrics
#   No one source has everything
def quarterlyMetric(filename):
    symbols = readFunds('SymbolsETF.csv')      #Get symbols of interest
    #symbols = readFunds('SymbolsETFDebug.csv')
    
    # Sort symbols & remove duplicates
    sortSymbols(symbols)

    # String to locate fund holdings
    URL = 'https://www.marketwatch.com/investing/fund/'

    dataList = []           # Allocate list to hold data
    hdrList = []            # Allocate list to hold header

    dateToday = date.today().strftime('%Y-%m-%d')
    count = True            # Build header
    
    for symbol in symbols.index:  # lookup data
        print(symbol)
        URLSym = URL + symbol

        try:
            yfData, yfDataHdr = yfGetQuarterlyMetrics(symbol)
            mwPage = procRequest(URLSym)
            mwKeyDataList, mwKeyDataHdr = mwGetKeyData(mwPage)

            symList = list(itertools.chain([dateToday], yfData, mwKeyDataList))
            dataList.append(symList)

            if(count == True):
                count = False
                hdrList = list(itertools.chain(['Date'], yfDataHdr, mwKeyDataHdr))
        except (IndexError, KeyError):
            dataList.append([dateToday, symbol])

    #Seralize data
    seralizeData(filename, dataList, hdrList)    # Seralize data

if __name__ == "__main__":
    import sys
    filename = 'quarterlyETFSymbols.xlsx'
    if(len(sys.argv) == 2):
        filename = sys.argv[1]

    quarterlyMetric(filename)
