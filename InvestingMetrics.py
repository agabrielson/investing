#!/usr/bin/env python
# coding: utf-8

# InvestingMetrics.py
#
# Rev History:
#   0.1     210425      New file - Merging similar code
#   0.15    210430      Change yf to get additional data
#   0.16    210512      Add getMetricsBulk to get significant data at once

import yfinance as yf
import numpy
import sys

from InvestingBase import startMonthYear, endMonthYear

# Try to figure out the monthly return for a symbol
#   Note: I suspect this method will become obsolete shortly...
def getMetrics(symbol, month, year):
    symDaily = "NA"
    dayFirst = "NA"
    dayEnd = "NA"

    month, year = startMonthYear(month, year)
    monthEnd, yearEnd = endMonthYear(month, year)

    start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    end = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)

    try:
        #Funds can do "1m" and get more data
        #   Stocks can do "1mo", which has much less data
        #   Want one metric function...
        #   Difference is "1mo" gets first day from month before and after
        #   "1d" gets alot more data, but sometimes "1mo" only wants first of the month
        symDaily = yf.download(symbol, start, end, interval="1d",progress=False)

        dayFirst = symDaily.iloc[0].Open
        dayEnd = symDaily.iloc[-1].Close

        if(numpy.isnan(dayEnd)):
            dayEnd = symDaily.iloc[-2].Close

        metricsList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]
    except:
        print("Unexpected error:", sys.exc_info()[0])
        metricsList = [symbol, " ", " ", " "]

    #intermediate values for debugging
    getMetrics.start = start
    getMetrics.end = end
    getMetrics.symDaily = symDaily
    getMetrics.dayFirst = dayFirst
    getMetrics.dayEnd = dayEnd

    return metricsList

# Try to figure out the monthly return for a symbol
#   Note: This will probably become the standard function, it will also probably be split up
#   Note: Yahoo Finance could be throttling this significantly...
#           Disabling threads to go a little slower, won't make a difference
def getMetricsBulk(symbols, month, year):
    symDaily = "NA"
    dayFirst = "NA"
    dayEnd = "NA"

    month, year = startMonthYear(month, year)
    monthEnd, yearEnd = endMonthYear(month, year)

    startDay = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    endDay = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)

    #Funds can do "1m" and get more data
    #   Stocks can do "1mo", which has much less data
    #   Want one metric function...
    #   Difference is "1mo" gets first day from month before and after
    #   "1d" gets alot more data, but sometimes "1mo" only wants first of the month
    sym = yf.download(symbols, startDay, endDay, interval="1d", 
        threads=False, group_by="ticker", actions=False)
 
    # Init empty container
    #counter = 0
    metricsList = []   #This is for the tickers being looked up
    prevSym = ''
    # breaking out aSym, var makes getting to data much easier
    #   It also duplicates symbols by 5x...
    for aSym, v1 in sym:
        if(prevSym == aSym):
            continue

        prevSym = aSym
        try:
            dayFirst = sym[aSym].iloc[0].Open
            dayEnd = sym[aSym].iloc[-1].Close

            if(numpy.isnan(dayEnd)):
                dayEnd = sym[aSym].iloc[-2].Close

            metricsList.append([aSym, dayFirst, dayEnd, dayEnd/dayFirst])
        except:
            print("Unexpected error:", sys.exc_info()[0])
            metricsList.append([aSym, " ", " ", " "])
            #counter+=1

    #print("Fail Count: %d" % counter)
    return metricsList
