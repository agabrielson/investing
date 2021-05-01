#!/usr/bin/env python
# coding: utf-8

# quartelyMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 quartelyMetrics.py              -> outputs in quarterlySymbols.xlsx
#   python3 quartelyMetrics.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1     210303      Initial Functionality
#                       Yahoo ytdReturn appears mistaken at times
#                       Would like to add Fund Manager
#   0.15    210410      Adding significantly more symbols
#   0.2     210418      Cleaning up code significantly
#   0.3     210426      Add Market Watch as a data source 
#                       Added significant number of fields
#                       Moving procRequest to InvestingBase
#   0.35    210501      Enhance symbol input

import yfinance as yf
import pandas as pd
import itertools 
from datetime import date
from InvestingBase import readFunds, procRequest, getDate, sortSymbols, seralizeData

def mwProcData(fullPage, searchStr):
    tableLoc = fullPage.find(searchStr)
    redPage = fullPage[tableLoc:]
    reduced = redPage.splitlines()

    return reduced[1]

def mwGetKeyData(fullPage): 
    tableLoc = fullPage.find('Key Data')
    yrRangeVal = mwProcData(fullPage[tableLoc:], '52 Week Range')
    fiveYrVal = mwProcData(fullPage[tableLoc:], '5 Year') 
    totAssetVal = mwProcData(fullPage[tableLoc:], 'Total Net Assets') 
    yieldVal = mwProcData(fullPage[tableLoc:], 'Yield')
    expenseRatioVal = mwProcData(fullPage[tableLoc:], 'Net Expense Ratio')
    turnoverVal = mwProcData(fullPage[tableLoc:], 'Turnover %')
    yrAvgRtnVal = mwProcData(fullPage[tableLoc:], '52 Week Avg Return')

    mwKeyDataList = [yrRangeVal, totAssetVal, fiveYrVal, yieldVal, expenseRatioVal, turnoverVal, yrAvgRtnVal]
    mwKeyDataHdr = ['52 Week Range', '5 Year', 'Total Net Assets', 'Yield',
                    'Net Expense Ratio', 'Turnover %', '52 Week Avg Return']
    return mwKeyDataList, mwKeyDataHdr

def mwGetReturns(fullPage):

    tableLoc = fullPage.find('Lipper Ranking & Performance')
    ytdVal = mwProcData(fullPage[tableLoc:], 'YTD')

    yr1Val = mwProcData(fullPage[tableLoc:], '1yr')
    yr3Val = mwProcData(fullPage[tableLoc:], '3yr')
    yr5Val = mwProcData(fullPage[tableLoc:], '5yr')

    mwPerfomanceList = [ytdVal, yr1Val, yr3Val, yr5Val]
    mwPerformanceHdr = ['YTD', '1yr', '3yr', '5yr']

    return mwPerfomanceList, mwPerformanceHdr

def mwGetRiskDetails(fullPage):
    alphaVal = mwProcData(fullPage, 'Alpha')
    betaVal = mwProcData(fullPage, 'Beta')
    stdVal = mwProcData(fullPage, 'Standard deviation')
    rsqVal = mwProcData(fullPage, 'R. squared')

    mwRiskList = [alphaVal, betaVal, stdVal, rsqVal]
    mwRiskHdr = ['Alpha', 'Beta', 'Standard deviation', 'R. squared']
    
    return mwRiskList, mwRiskHdr

def mwGetFundDetails(fullPage):
    inception = mwProcData(fullPage, 'Fund Inception')
    manager = mwProcData(fullPage, 'Manager')

    mwFundList = [inception, manager]
    mwFundHdr = ['Fund Inception','Manager']

    return mwFundList, mwFundHdr

def yfGetQuarterlyMetrics(symbol):
    sym = yf.Ticker(symbol)
    
    sName = sym.info['symbol']
    lName = sym.info['longName']
    
    sustain = '-'
    if(sym.sustainability is not None):
        sustain = sym.sustainability['Value'].to_dict()['peerGroup']
    mstarOver = sym.info['morningStarOverallRating']
    mstarRisk = sym.info['morningStarRiskRating']
    
    yfDataList = [sName, lName, mstarOver, mstarRisk, sustain]
    yfDataHdr = ['Symbol', 'Name', 'Morningstar Overall', 'morningStar Risk', 'Peer Group']

    return yfDataList, yfDataHdr

# Lookup quartely metrics
#   No one source has everything
#   Some of the yahoo data appears to be suspect
#   Going to pull suspect and missing data points from MarketWatch
#   Then merge the two data sources
def quarterlyMetric(filename):
    symbols = readFunds('Symbols.csv')      #Get symbols of interest
    #symbols = readFunds('SymbolsDebug.csv')
    
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
            mwPerfomanceList, mwPerformanceHdr = mwGetReturns(mwPage)
            mwRiskList, mwRiskHdr = mwGetRiskDetails(mwPage)
            mwFundList, mwFundHdr = mwGetFundDetails(mwPage)

            symList = list(itertools.chain([dateToday], yfData, mwKeyDataList, mwPerfomanceList, mwRiskList, mwFundList))
            dataList.append(symList)

            if(count == True):
                count = False
                hdrList = list(itertools.chain(['Date'], yfDataHdr, mwKeyDataHdr, mwPerformanceHdr, mwRiskHdr, mwFundHdr))
        except:
            dataList.append([dateToday, symbol])

    #Seralize data
    seralizeData(filename, dataList, hdrList)    # Seralize data

if __name__ == "__main__":
        import sys
        filename = 'quarterlySymbols.xlsx'
        if(len(sys.argv) == 2):
            filename = sys.argv[1]

        quarterlyMetric(filename)
