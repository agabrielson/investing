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
#   0.15    210724      Moving mwGetName to InvestingBase

import pandas as pd
import itertools 
from datetime import date
from InvestingBase import readFunds, procRequest, getDate, sortSymbols, seralizeData, stripHTML, mwGetName, mwProcData

# mwGetKeyData: Extract the info from the key data table
# Inputs
#   fullPage: page to look through
# Returns
#   mwKeyDataList: The data points of interest from the table
#   mwKeyDataHdr: Header data for points of interest
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

# yfProcData: Extract values of interest from a scraped webpage
#   This function is a bit targetted for etfdb
# Inputs
#   fullPage: page to look through
#   searchStrS: string before data point of interest
#   searchStrE: string after data point of interest
# Returns
#   Value between the two search strings
def yfProcData(fullPage, searchStrS, searchStrE):
    tableLocSrt = fullPage.find(searchStrS)+len(searchStrS)
    redPage = fullPage[tableLocSrt:]

    tableLocEnd = redPage.find(searchStrE)
    redPage = redPage[:tableLocEnd]

    #print('yfDP: ' + str(tableLocSrt) + ' ' + str(tableLocEnd))
    #print('Search Start: ' + searchStrS)
    #print('Search End: ' + searchStrE)
    #print(fullPage)
    #print(fullPage[tableLocSrt:])
    #print('yfRet: ' + redPage)

    return redPage.strip()

# yfPerformance: Extract the data points of interest
# Inputs
#   fullPage: page to look through
# Returns
#   yfKeyDataList: The data points of interest from the table
#   dbKeyDataHdr: Header data for points of interest
def yfPerformance(fullPage):
    tableLocS = fullPage.find('Vs. Benchmarks')
    fp = fullPage[tableLocS:]
    tableLocE = fp.find('Annual Total Return')
    fp = fp[:tableLocE]
    fp = stripHTML(fp)
    entry = ' '.join([str(elem) for elem in fp])

    ytdRtn = yfProcData(entry, 'YTD', '%')
    rtn1yr = yfProcData(entry, '1-Year', '%')
    rtn3yr = yfProcData(entry, '3-Year', '%')
    rtn5yr = yfProcData(entry, '5-Year', '%')

    yfPerfDataList = [ytdRtn, rtn1yr, rtn3yr, rtn5yr]
    yfPerfDataHdr = ['YTD Rtn', '1 Yr Rtn', '3 Yr Rtn', '5 Yr Rtn']

    return yfPerfDataList, yfPerfDataHdr

# yfProfile: Extract the data points of interest
# Inputs
#   fullPage: page to look through
# Returns
#   yfProData: The data points of interest from the table
#   yfProDataHdr: Header data for points of interest
def yfProfile(fullPage):
    tableLocS = fullPage.find('Fund Overview')+len('Fund Overview')
    fp = fullPage[tableLocS:]
    tableLocE = fp.find('Fund Operations')+len('Fund Operations')
    fp = fullPage[tableLocS:]
    fp = fp[:tableLocE]
    fp = stripHTML(fp)
    entry = ' '.join([str(elem) for elem in fp]) 

    cat = yfProcData(entry, 'Category', 'Fund Family')
    classSz = yfProcData(entry, 'Net Assets', 'YTD Daily Total Return')

    tableLocS = fullPage.find('Fund Operations')+len('Fund Operations')
    fp = fullPage[tableLocS:]
    tableLocE = fp.find('Total Net Assets')+len('Total Net Assets')
    fp = fullPage[tableLocS:]
    fp = fp[:tableLocE]
    fp = stripHTML(fp)
    entry = ' '.join([str(elem) for elem in fp]) 

    turnover = yfProcData(entry, 'Holdings Turnover', '%')

    yfProData = [cat, classSz, turnover]
    yfProDataHdr = ['Category', 'Asset Class Size', 'Turnover']

    return yfProData, yfProDataHdr

# Lookup quartely metrics
#   No one source has everything
def quarterlyETFMetric(filename):
    symbols = readFunds('SymbolsETF.csv')      #Get symbols of interest
    #symbols = readFunds('SymbolsETFDebug.csv')
    
    # Sort symbols & remove duplicates
    sortSymbols(symbols)

    # String to locate fund holdings
    MW_URL = 'https://www.marketwatch.com/investing/fund/'
    YF_URL_p1 = 'https://finance.yahoo.com/quote/'
    YF_URL_p2 = '/performance'
    YF_URL_p3 = '/profile'

    dataList = []           # Allocate list to hold data
    hdrList = []            # Allocate list to hold header

    dateToday = date.today().strftime('%Y-%m-%d')
    count = True            # Build header

    headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36' } 

    for symbol in symbols.index:  # lookup data
        print(symbol)
        MW_URLSym = MW_URL + symbol.strip()
        YF1_URLSym= YF_URL_p1 + symbol.strip() + YF_URL_p2
        YF2_URLSym= YF_URL_p1 + symbol.strip() + YF_URL_p3
        
        # Prealloc storage variables
        mwKeyDataList = '' 
        mwKeyDataHdr = ''
        yfPerfData = ''
        yfPerfDataHdr = ''
        yfProData = ''
        yfProDataHdr = ''

        try:
            mwPage = procRequest(MW_URLSym)
            nameLong, closed = mwGetName(mwPage)
            if(closed is False):
                mwKeyDataList, mwKeyDataHdr = mwGetKeyData(mwPage)
            
                yfPage = procRequest(YF1_URLSym, 5, False, headers=headers)
                yfPerfData, yfPerfDataHdr = yfPerformance(yfPage)

                yfPage = procRequest(YF2_URLSym, 5, False, headers=headers)
                yfProData, yfProDataHdr = yfProfile(yfPage)

                symList = list(itertools.chain([dateToday], [symbol], [nameLong], mwKeyDataList, yfPerfData, yfProData))
                dataList.append(symList)
            else:
                dataList.append([dateToday, symbol, 'closed'])

            if(count == True):
                count = False
                hdrList = list(itertools.chain(['Date'], ['Symbol'], ['Long Name'], mwKeyDataHdr, yfPerfDataHdr, yfProDataHdr))
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
