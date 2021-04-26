#!/usr/bin/env python
# coding: utf-8

# InvestingMetrics.py
#
# Rev History:
#   0.1     210425      New file - Merging similar code

import yfinance as yf
import numpy

from InvestingBase import startMonthYear, endMonthYear

# Try to figure out the monthly return for a symbol
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
        symDaily = yf.download(symbol, start, end, interval="1mo",progress=False)

        dayFirst = symDaily.iloc[0].Close
        dayEnd = symDaily.iloc[-1].Close

        if(numpy.isnan(dayEnd)):
            dayEnd = symDaily.iloc[sdLen-2].Close

        metricsList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]
    except:
        metricsList = [symbol, " ", " ", " "]

    #intermediate values for debugging
    getMetrics.symDaily = symDaily
    getMetrics.dayFirst = dayFirst
    getMetrics.dayEnd = dayEnd

    return metricsList



