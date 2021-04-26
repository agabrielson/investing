#!/usr/bin/env python
# coding: utf-8

# InvestingBase.py
#
# Rev History:
#   0.1		210418		New file - cleaning up similar code
#	0.2		210426		Add procRequest & standardize

from datetime import date
import pandas as pd
import requests
import re 

from bs4 import BeautifulSoup

# Make a request and start to reduce the string
#   We are only interested in the table with holdings information
def procRequest(URLSym):
    page = requests.get(URLSym)
    soup = BeautifulSoup(page.content, 'html.parser')
    fullPage = soup.get_text();

    #Remove space
    fullPage = re.sub(r'\n\s*\n', '\n', fullPage, flags=re.MULTILINE)

    return fullPage

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
