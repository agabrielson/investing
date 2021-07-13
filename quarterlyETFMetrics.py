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
    avgVol = mwProcData(fullPage[tableLoc:], 'Average Volume')

    mwKeyDataList = [yrRangeVal, totAssetVal, yieldVal, expenseRatioVal, turnoverVal, div, divDate, avgVol]
    mwKeyDataHdr = ['52 Week Range', 'Total Net Assets', 'Yield', 'Net Expense Ratio', 'Turnover %', 'Dividend', 
                    'Ex-Dividend Date', 'AVG Vol']

    return mwKeyDataList, mwKeyDataHdr

def dbProcData(fullPage, searchStrS, searchStrE):
    tableLocSrt = fullPage.find(searchStrS)+len(searchStrS)
    tableLocEnd = fullPage.find(searchStrE)
    redPage = fullPage[tableLocSrt:tableLocEnd]
    reduced = redPage.splitlines()

    if (len(reduced) == 1):
        return None

    return reduced[1]

def dbGetKeyData1(fullPage):
    ytdRtn = dbProcData(fullPage, '26 Week Return', 'Year to Date Return')
    rtn1yr = dbProcData(fullPage, 'Year to Date Return', '1 Year Return')
    rtn3yr = dbProcData(fullPage, '1 Year Return', '3 Year Return')
    rtn5yr = dbProcData(fullPage, '3 Year Return', '5 Year Return')

    dbKeyDataList = [ytdRtn, rtn1yr, rtn3yr, rtn5yr]
    dbKeyDataHdr = ['YTD Rtn', '1 Yr Rtn', '3 Yr Rtn', '5 Yr Rtn']

    return dbKeyDataList, dbKeyDataHdr

def dbGetKeyData2(fullPage):
    tableLoc = fullPage.find('Investment Themes')
    cat = dbProcData(fullPage[tableLoc:], 'Category', 'Asset Class')
    aClass = dbProcData(fullPage[tableLoc:], 'Asset Class', 'Asset Class Size')
    classSz = dbProcData(fullPage[tableLoc:], 'Asset Class Size', 'Asset Class Style<')

    dbKeyDataList = [cat, aClass, classSz]
    dbKeyDataHdr = ['Category', 'Asset Class', 'Asset Class Size']

    return dbKeyDataList, dbKeyDataHdr

def yfGetQuarterlyMetrics(symbol):
    sym = yf.Ticker(symbol)
    
    sName = sym.info['symbol']
    lName = sym.info['longName']

    totAssets = sym.info['totalAssets']
    yieldVal = sym.info['yield']
    trailYield = sym.info['trailingAnnualDividendYield']

    yfDataList = [sName, lName, totAssets, yieldVal, trailYield]
    yfDataHdr = ['Symbol', 'Name', 'Total Assets', 'yield', 'Trailing Annual Dividend Yield']

    return yfDataList, yfDataHdr

# Lookup quartely metrics
#   No one source has everything
def quarterlyMetric(filename):
    #symbols = readFunds('SymbolsETF.csv')      #Get symbols of interest
    symbols = readFunds('SymbolsETFDebug.csv')
    
    # Sort symbols & remove duplicates
    sortSymbols(symbols)

    # String to locate fund holdings
    MW_URL = 'https://www.marketwatch.com/investing/fund/'
    DB_URL_p1 = 'https://etfdb.com/etf/'
    DB_URL_p2 = '/#performance'
    DB_URL_p3 = '/#etf-ticker-profile'

    dataList = []           # Allocate list to hold data
    hdrList = []            # Allocate list to hold header

    dateToday = date.today().strftime('%Y-%m-%d')
    count = True            # Build header
    
    for symbol in symbols.index:  # lookup data
        print(symbol)
        MW_URLSym = MW_URL + symbol
        DB1_URLSym= DB_URL_p1 + symbol + DB_URL_p2
        DB2_URLSym= DB_URL_p1 + symbol + DB_URL_p3
        
        try:
            yfData, yfDataHdr = yfGetQuarterlyMetrics(symbol)
            
            mwPage = procRequest(MW_URLSym, 5, True, allow_redirects=False)
            mwKeyDataList, mwKeyDataHdr = mwGetKeyData(mwPage)

            dbPage = procRequest(DB1_URLSym, 5, True, allow_redirects=False)
            dbKeyDataList1, dbKeyDataHdr1 = dbGetKeyData1(dbPage)

            dbPage = procRequest(DB2_URLSym, 5, True, allow_redirects=False)
            dbKeyDataList2, dbKeyDataHdr2 = dbGetKeyData2(dbPage)

            symList = list(itertools.chain([dateToday], yfData, mwKeyDataList, dbKeyDataList1, dbKeyDataList2))
            dataList.append(symList)

            if(count == True):
                count = False
                hdrList = list(itertools.chain(['Date'], yfDataHdr, mwKeyDataHdr, dbKeyDataHdr1, dbKeyDataHdr2))
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
