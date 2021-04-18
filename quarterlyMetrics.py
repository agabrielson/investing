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
#   0.1 - 210303
#           Initial Functionality
#           Yahoo ytdReturn appears mistaken at times
#           Would like to add Fund Manager
#   0.15 - 210410
#           Adding significantly more symbols

import yfinance as yf
import pandas as pd
import datetime as dt

from interestingFunds import interestingFunds

# What should be added?
#   Fund Manager

def getDate():
    dateTimeList = []
    today = dt.date.today()
    dateTimeList.append(today)
    return dateTimeList[0]

def getQuarterlyMetrics(symbol):
    sym = yf.Ticker(symbol)
    
    dateToday = getDate()
    sName = sym.info['symbol']
    lName = sym.info['longName']
    
    sustain = '-'
    if(sym.sustainability is not None):
        sustain = sym.sustainability['Value'].to_dict()['peerGroup']
        
    mstar = sym.info['morningStarRiskRating']
    expRatio = round(sym.info['annualReportExpenseRatio'],2)
    ytdRtn = round(sym.info['ytdReturn'],2)
    
    beta3 = "-"
    if(sym.info["beta3Year"] is not None):
        beta3 = round(sym.info['beta3Year'],2)
    
    totAss = round(sym.info['totalAssets']/(1000000),0) 
    turn = round(sym.info['annualHoldingsTurnover'],2)
    
    dataList = [dateToday, sName, lName, sustain, mstar, expRatio, ytdRtn, beta3, totAss, turn]
   
    return dataList

def quarterlyMetric(filename):
    symbols = interestingFunds()    #Get symbols of interest
    #symbols = ['FSMEX']

    # Sort symbols & remove duplicates
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    symbols = res

    
    dataList = []           # Allocate list to hold data 
    dateToday = getDate()
    for symbol in symbols:  # lookup data
        print(symbol)
        try:
            dataList.append(getQuarterlyMetrics(symbol))
        except:
            dataList.append([dateToday, symbol])

    #Seralize data
    df = pd.DataFrame (dataList,columns=['Date', 'Symbol', 'Long Name', 'Peer Group', 'Morningstar',
                                        'Exp Ratio', 'YTD Return(?!)', 'beta3', 'Total Assets ($M)',
                                        'Turnover'])
    #print(df)
    df.to_excel(filename)

if __name__ == "__main__":
        import sys
        filename = 'quarterlySymbols.xlsx'
        if(len(sys.argv) == 2):
            filename = sys.argv[1]

        quarterlyMetric(filename)
