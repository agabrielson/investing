#!/usr/bin/env python
# coding: utf-8

# getStocks.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#	year:		year to collect data points for, can be left blank
#
# Examples
#   python3 getStocks.py               -> outputs in stockData.xlsx
#   python3 getStocks.py data.xlsx     -> outputs in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 getStocks.py march.xlsx 3
#       Notes: Collect data for March of this year, outputs in march.xlsx 
#   python3 getStocks.py dec2020.xlsx 12 2020
#
# Rev History:
#	0.1     210512		Initial Functionality

import yfinance as yf
import pandas as pd
import requests
import json
import numpy as np

from InvestingBase import seralizeData, procStocks, extractTicker
from InvestingMetrics import getMetricsBulk

# Get stock metrics for a given month
def stockMetrics(filename, month, year):
	# SEC hosts JSON file with every ticker in the US
	URLSym = 'https://www.sec.gov/files/company_tickers.json'
	stocksJson = procStocks(URLSym)		# Obtain all tickers in JSON

	symList = extractTicker(stocksJson) # We just need the ticker symbol for this script
	#symList = ['TSLA', 'FB', 'YUM']

	symbolsData = getMetricsBulk(symList, month, year)	# Get data for symbol in bulk

	cols = ['Symbol','First', 'Last', 'Monthly Rtn']
	seralizeData(filename, symbolsData, cols)			# Serialize data


if __name__ == "__main__":
	import sys

	year = None							# month to lookup
	if(len(sys.argv) >= 4):
		year = sys.argv[3]

	month = None						# month to lookup
	if(len(sys.argv) >= 3):
		month = sys.argv[2]

	filename = 'stockData.xlsx'
	if(len(sys.argv) == 2):
		filename = sys.argv[1]

	stockMetrics(filename, month, year)
