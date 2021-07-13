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
#   0.11    210713      Reducing depends - YF.Ticker() has issues with ETFs, few show up...

#import yfinance as yf
import pandas as pd
import itertools 
#import requests
from datetime import date
from InvestingBase import readFunds, procRequest, getDate, sortSymbols, seralizeData

def mwProcData(fullPage, searchStr):
    tableLoc = fullPage.find(searchStr)
    redPage = fullPage[tableLoc:]
    reduced = redPage.splitlines()

    if (len(reduced) == 1):
        return None

    return reduced[1]

def mwGetName(fullPage, symbol):
    closed = False

    fp = fullPage.splitlines()
    nameLong = fp[1]
    totStrStart = nameLong.find('|')+2
    nameLong = nameLong[totStrStart:]
    totStrEnd = nameLong.find('Overview')-1
    nameLong = nameLong[:totStrEnd]

    NAVDate = mwProcData(fullPage, 'NAV Date')
    if(NAVDate == 'N/A'):
        closed = True

    return nameLong, closed

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

# Lookup quartely metrics
#   No one source has everything
def quarterlyETFMetric(filename):
    symbols = readFunds('SymbolsETF.csv')      #Get symbols of interest
    #symbols = readFunds('SymbolsETFDebug.csv')
    
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
    
    #agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    #header = requests.utils.default_headers()
    #header['User-Agent'] = agent;
    #print(headers)

    for symbol in symbols.index:  # lookup data
        print(symbol)
        MW_URLSym = MW_URL + symbol.strip()
        DB1_URLSym= DB_URL_p1 + symbol.strip() + DB_URL_p2
        DB2_URLSym= DB_URL_p1 + symbol.strip() + DB_URL_p3
        
        try:
            mwPage = procRequest(MW_URLSym, 5, True, allow_redirects=True)
            nameLong, closed = mwGetName(mwPage, symbol)
            if(closed is False):
                mwKeyDataList, mwKeyDataHdr = mwGetKeyData(mwPage)
            
                dbPage = procRequest(DB1_URLSym, 5, True, allow_redirects=True)
                dbKeyDataList1, dbKeyDataHdr1 = dbGetKeyData1(dbPage)

                dbPage = procRequest(DB2_URLSym, 5, True, allow_redirects=True)
                dbKeyDataList2, dbKeyDataHdr2 = dbGetKeyData2(dbPage)

                symList = list(itertools.chain([dateToday], [symbol], [nameLong], mwKeyDataList, dbKeyDataList1, dbKeyDataList2))
                dataList.append(symList)
            else:
                dataList.append([dateToday, symbol, 'closed'])

            if(count == True):
                count = False
                hdrList = list(itertools.chain(['Date'], ['Symbol'], ['Long Name'], mwKeyDataHdr, dbKeyDataHdr1, dbKeyDataHdr2))
        except (IndexError, KeyError):
            dataList.append([dateToday, symbol])

    #Seralize data
    seralizeData(filename, dataList, hdrList)    # Seralize data

if __name__ == "__main__":
    import sys
    filename = 'quarterlyETFSymbols.xlsx'
    if(len(sys.argv) == 2):
        filename = sys.argv[1]

    quarterlyETFMetric(filename)
