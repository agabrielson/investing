#!/usr/bin/env python
# coding: utf-8

# getHoldings.py
#
# Inputs
#	investType:	Investment type -> fund or ETF
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#	year:		year to collect data points for, can be left blank
#
# Examples
#   python3 getHoldings.py               -> outputs in fundSymbols.xlsx
#   python3 getHoldings.py etf           -> outputs etfs in etfSymbols.xlsx
#   python3 getHoldings.py fund data.xlsx-> outputs funds in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 getHoldings.py etf march.xlsx 3
#       Notes: Collect etf data for March of this year, outputs in march.xlsx 
#   python3 getHoldings.py fund dec2020.xlsx 12 2020
#
# Rev History:
#	0.1     210411		Initial Functionality
#	0.15	210412		Fixed hardcode bug in getTuble (%)
#						Fixed yfinance return bug, an extra row with nan...
#	0.16	210413		General code documentation, clean up, and variable rename for sanity
#	0.2     210418		Cleaning up code significantly
#	0.3		210425		Look up holdings symbols once
#						Fixed a bug with symbol names (<=2 were skipped)
#						Disabled yf progress on screen
#   0.32    210425      InvestingMetrics - moved getMetrics
#	0.33	210426		InvestingBase - moved procRequest
#						Adjusted code for standardized procRequest
#	0.35	210501		Enhance symbol input
#	0.4 	210726		Switch between funds & ETFs

import numpy
import re 
import pandas as pd

from InvestingBase import readFunds, procRequest, sortSymbols, seralizeData, mwGetName
from InvestingMetrics import getMetrics

# Let's lookup each symbol once...
#	Make a call to get month return for a given period
def lookupSymbol(symbol, month, year):
	# With fund symbol information, let's get the 
	monthRtnStr = ""
	if(symbol.find(" ")):
		symMetrics = getMetrics(symbol, month, year)	# look up return for a symbol
		monthRtn = symMetrics[3]
		if monthRtn != " ":
			monthRtnList = ("%.4f" % monthRtn)
			monthRtnStr = " "
			monthRtnStr = monthRtnStr.join(monthRtnList).replace(" ","")

	return monthRtnStr

# Process the specific holdings
#	(Company, Symbol, Total Net Assets)
#	Note: Note all symbols are on the exchange...
def getSpecificHolding(str):
	# Locate percent at the end of each holding line
	percLocStart = re.search("\d+(\.\d\d%|\s\bpercent\b)",str).start()
	percLocEnd = str[percLocStart:].find("%")+1

	fundPerc = ""
	fundPerc = str[percLocStart:percLocStart+percLocEnd]
	str = str[0:percLocStart-1]

	li = str.splitlines()

	companyName = ""
	companySymbol = ""
	ctr = 0
	for ln in li:
		if (len(ln) > 0) and (ctr == 0):
			companyName = ln 	# Company/Fund name is never blank
			ctr = ctr + 1
		else:
			companySymbol = ln 	# Symbol is often blank...

	companySymbol = companySymbol.replace(" ","")	# Eliminate needless symbols
	companySymbol = companySymbol.replace(".", "-")	# yahoo has a few different characters in lookup
	holding = [companyName, companySymbol, fundPerc]

	return holding 

# Put together the holdings list
#	find the table holding all data
def mwBuildHoldings(fullPage):
	# Find first and last deliminiter
	#	Table start deliminiter
	tableLoc = fullPage.find('Top 10 Holdings')
	if(tableLoc == -1):
		tableLoc = fullPage.find('Top 25 Holdings')

	fullPage = fullPage[tableLoc:]

	# Find As Of & last deliminiter (end of table)
	matchAsOf = fullPage.find("As of")	# Pull out As of 01/31/2021
	asOf = fullPage[matchAsOf:matchAsOf+16]
	
	# Find first deliminiter (start of table)
	matchStart = fullPage.find("Total Net Assets")+len("Total Net Assets")
	
	# This string has all holdings, need to get individual holdings
	fullPage = fullPage[matchStart:matchAsOf-1]

	# Init empty containers
	holdingsList = []	#This is for the specific fund
	holdingsDict = {}	#This will be for a mass lookup

	iterCnt = True
	while iterCnt == True:
		try:	# Look for the percentage (3rd col)
			percLoc = re.search("\d+(\.\d\d%|\s\bpercent\b)",fullPage).start()+5
		except:	# Give if it doesn't exist
			iterCnt = False
			break

		# Really give up if it doesn't exist
		if(type(percLoc) == None) or (percLoc == -1):
			iterCnt = False
			break

		substr = fullPage[0:percLoc+1] 		# One line from the table
		holding = getSpecificHolding(substr)	# Extract the 2-3 values
		matchStart = percLoc+2					# Enable the regex to find the next 'x.xx%'
		
		fullPage = fullPage[percLoc+1:matchAsOf-1]
		holding += [" "]	# add an empty field as a placeholder
		holdingsList.append(holding)

	for i in holdingsList:
		holdingsDict[i[1]] = None

	return holdingsList, holdingsDict, asOf

from requests_html import HTMLSession
from bs4 import BeautifulSoup

# Placeholder. It would eventually be nice to get iShare ETF holdings directly 
#	from iShare Right now, the data doesn't come through... Other paths may 
#	exist, but this will need to be revisited.
def iShareBuildHoldings(symbol):
	holdingsList = ''
	holdingsDict = ''
	asOf = ''

	#https://www.ishares.com/us/search/summary-results?searchText=ivv&doTickerSearch=true
	#iShareURL_P1 = 'https://www.ishares.com/us/search/summary-results?searchText='
	#iShareURL_P2 = 'doTickerSearch=true'
	#iShareURL = 'https://www.ishares.com//'

	# This link will get json:
	#	https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?tab=all&fileType=json
	# Need to abstract based on ticker symbol

	#URL = iShareURL + symbol

	return holdingsList, holdingsDict, asOf	

# Put together the holdings list
#	find the table holding all data
def buildHoldings(fullPage, symbol):
	holdingsList = ''
	holdingsDict = ''
	asOf = ''

	# Get name of the fund and if open
	nameLong, closed = mwGetName(fullPage)
	if(closed == True):
		return holdingsList, holdingsDict, asOf, closed

	#if('iShares' in nameLong):
	#	print('iShares ETF: ' + nameLong)
	#	holdingsList, holdingsDict, asOf = iShareBuildHoldings(symbol)
	#else:
	holdingsList, holdingsDict, asOf = mwBuildHoldings(fullPage)

	return holdingsList, holdingsDict, asOf, closed

# We need to bring the holdingsDict Value data back into the symbols data list
def mergeDictList(holdingsDict, symbolsData):
	for symbol in holdingsDict:
		for n, i in enumerate(symbolsData):
			if((len(i) > 2) and (symbol == i[2])):
				i[4] = holdingsDict[symbol]

# Main
def getHoldings(investType, filename, month, year):
	# Get symbols of interest & sort -> Update Fund vs ETF
	if(investType.lower().strip() == 'fund'):
		symbols = readFunds('Symbols.csv')
		#symbols = readFunds('SymbolsDebug.csv')
	elif(investType.lower().strip() == 'etf'):
		symbols = readFunds('SymbolsETF.csv')
		#symbols = readFunds('SymbolsETFDebug.csv')
	else:
		print('Type should be fund or etf')
		return
	
	sortSymbols(symbols)      # Sort symbols & remove duplicates

	# String to locate fund holdings
	URL = 'https://www.marketwatch.com/investing/fund/'
	URLLong = '/holdings'

	# prealloc container
	holdingsDict = {}
	symbolsData = [] 

	# top of the spreadsheet
	symbolsData.append(['Fund','Company','Symbol','Total Net Assets','Monthly Rtn'])
	# Build the list of holdings for each fund
	for symbol in symbols.index:
		print(symbol)
		URLSym = URL + symbol.strip()
		#URLSym += URLLong 		#Get top 25 instead of top 10
		
		# Lookup the holdings
		pageProc = procRequest(URLSym)
		holdings = " "
		holdings, hDictSub, asOf, closed = buildHoldings(pageProc, symbol)
		if(closed == True):
			print('closed')
			strList = [symbol] + ['closed']
		else:
			holdingsDict.update(hDictSub)	#Merge dictionaries - one lookup
			strList = [symbol] + [asOf]

		# Build table to serialize, note mergeDict will add value info
		symbolsData.append(strList)
		for i in holdings:
			symbolsData.append([" "] + i)
	
	#Lookup holdings
	for symbol in holdingsDict:
		holdingsDict[symbol] = lookupSymbol(symbol, month, year)
		print(symbol, "\t->\t", holdingsDict[symbol])
	
	# Add value info into the symbolsData
	mergeDictList(holdingsDict, symbolsData) # merge symbol returns into list

	seralizeData(filename, symbolsData)

if __name__ == "__main__":
    import sys

    investType = 'fund'
    if(len(sys.argv) >= 2):
    	investType = sys.argv[1]

    filename = 'etfHoldings.xlsx'		# File name to seralize data
    if(investType == 'fund'):
    	filename = 'fundHoldings.xlsx'

    if(len(sys.argv) >= 3):
    	filename = sys.argv[2]

    month = None						# month to lookup
    if(len(sys.argv) >= 4):
    	month = sys.argv[3]

    year = None							# month to lookup
    if(len(sys.argv) >= 5):
    	year = sys.argv[4]

    getHoldings(investType, filename, month, year)
