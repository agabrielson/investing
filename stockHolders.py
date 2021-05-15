#!/usr/bin/env python
# coding: utf-8

# stockHolders.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 stockHolders.py               -> outputs in interestSymbols.xlsx
#   python3 stockHolders.py data.xlsx     -> outputs in data.xlsx
#
# Rev History:
#	0.1     210515		Initial Functionality

import pandas as pd
import yfinance as yf

from InvestingBase import procStocks, extractTicker, seralizeData

# Get specific stock holdings
#	(Holder, Shares, Report Date, Out, Value)
def getStockHolders(symbol):
	holders = [] 

	stock = yf.Ticker(symbol)

	count = 0
	ihLen = len(stock.institutional_holders)
	while count < ihLen:
		holder = stock.institutional_holders.iloc[count,0]
		shares = stock.institutional_holders.iloc[count,1]
		reported = stock.institutional_holders.iloc[count,2].strftime('%Y-%m-%d')
		out = stock.institutional_holders.iloc[count,3]
		val = stock.institutional_holders.iloc[count,4]
		holders.append(["", holder, shares, reported, out, val])
		count+=1

	return holders

# Main
def getHolders(filename):
	# Get symbols of interest (all US symbols)
	URLSym = 'https://www.sec.gov/files/company_tickers.json'
	stocksJson = procStocks(URLSym)		# Obtain all tickers in JSON

	symList = extractTicker(stocksJson) # We just need the ticker symbol for this script
	#symList = ['TSLA', 'FB', 'YUM']

	# prealloc container
	holderData = [] 

	# top of the spreadsheet
	holderData.append(['Symbol','Holder', 'Shares', 'Report Date', 'Out', 'Value'])
	# Build the list of holdings for each fund
	for symbol in symList:
		print(symbol)
		
		holderData.append([symbol])
		symData = getStockHolders(symbol)
		for iSym in symData:
			holderData.append(iSym)

	seralizeData(filename, holderData)

if __name__ == "__main__":
    import sys

    filename = 'stockHolders.xlsx'		# File name to seralize data
    if(len(sys.argv) >= 2):
    	filename = sys.argv[1]

    getHolders(filename)
