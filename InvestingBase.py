#!/usr/bin/env python
# coding: utf-8

# InvestingBase.py
#
# Rev History:
#   0.1     210418      New file - cleaning up similar code

from datetime import date
import pandas as pd

# Verify month and year are sane
def startMonthYear(month, year):
	if year is None:
		year = date.today().year

	if isinstance(year, str):
		year = int(year)

	if month is None:
		month = date.today().month - 1

	if isinstance(month, str):
		month = int(month)

	return month, year;

# Wrap around month as needed
def endMonthYear(month, year):
	month, year = startMonthYear(month, year)
	month = month + 1
	if month == 13:
		month = 1
		year = year + 1

	return month, year;

def getDate():
    dateTimeList = []
    today = date.today()
    dateTimeList.append(today)
    return dateTimeList[0]

# Deduplicate symbols and sort them
def sortSymbols(symbols):
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    return res

# Write data to the filesystem
def seralizeData(filename, dataList, cols = None):
	df = pd.DataFrame(dataList, columns=cols)
	df.to_excel(filename)
