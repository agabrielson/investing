#!/usr/bin/env python
# coding: utf-8

# getHoldings.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#	year:		year to collect data points for, can be left blank
#
# Examples
#   python3 getHoldings.py               -> outputs in interestSymbols.xlsx
#   python3 getHoldings.py data.xlsx     -> outputs in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 getHoldings.py march.xlsx 3
#       Notes: Collect data for March of this year, outputs in march.xlsx 
#   python3 getHoldings.py dec2020.xlsx 12 2020
#
# Rev History:
#   0.1     210411      Initial Functionality
#	0.15	210412		Fixed hardcode bug in getTuble (%)
#						Fixed yfinance return bug, an extra row with nan...
#	0.16	210413 		General code documentation, clean up, and variable rename for sanity
#   0.2     210418      Cleaning up code significantly

import yfinance as yf
import requests
import re 
import numpy
from bs4 import BeautifulSoup

from interestingFunds import interestingFunds
from InvestingBase import startMonthYear, endMonthYear, sortSymbols, seralizeData

# Try to figure out the monthly return for a symbol
def getMetrics(symbol, month, year):
	month, year = startMonthYear(month, year)
	monthEnd, yearEnd = endMonthYear(month, year)

	start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
	end = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)
	try:
		symDaily = yf.download(symbol, start, end, interval="1mo")
		#print(symDaily)
		dayFirst = symDaily.iloc[0].Close

		sdLen = len(symDaily)
		dayEnd = symDaily.iloc[-1].Close
		if(numpy.isnan(dayEnd)):
			dayEnd = symDaily.iloc[sdLen-2].Close

		metricsList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]
	except:
		metricsList = [symbol, " ", " ", " "]
	
	return metricsList

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
#	Make a call to get month return for a given period
def buildHoldings(reducedStr, month, year):
	# Find As Of & last deliminiter (end of table)
	matchAsOf = reducedStr.find("As of")	# Pull out As of 01/31/2021
	asOf = reducedStr[matchAsOf:matchAsOf+16]
	
	# Find first deliminiter (start of table)
	matchStart = reducedStr.find("Total Net Assets")+len("Total Net Assets")
	
	# This string has all holdings, need to get individual holdings
	reducedStr = reducedStr[matchStart:matchAsOf-1]

	holdingsList = []
	iterCnt = True
	while iterCnt == True:
		try:	# Look for the percentage (3rd col)
			percLoc = re.search("\d+(\.\d\d%|\s\bpercent\b)",reducedStr).start()+5
		except:	# Give if it doesn't exist
			iterCnt = False
			break

		# Really give up if it doesn't exist
		if(type(percLoc) == None) or (percLoc == -1):
			iterCnt = False
			break

		substr = reducedStr[0:percLoc+1] 		# One line from the table
		holding = getSpecificHolding(substr)	# Extract the 2-3 values
		matchStart = percLoc+2					# Enable the regex to find the next 'x.xx%'
		
		# With fund symbol information, let's get the 
		if(len(holding) > 2) and (holding[1].find(".")) and (holding[1].find(" ")):
			dl = getMetrics(holding[1], month, year)	# look up return for a symbol
			monthRtn = dl[3]
			if monthRtn != " ":
				monthRtnList = ("%.4f" % monthRtn)
				monthRtnStr = " "
				monthRtnStr = monthRtnStr.join(monthRtnList).replace(" ","")
				holding += [monthRtnStr]
		
		reducedStr = reducedStr[percLoc+1:matchAsOf-1]
		holdingsList.append(holding)

	return holdingsList, asOf

# Make a request and start to reduce the string
#	We are only interested in the table with holdings information
def procRequest(page):
	soup = BeautifulSoup(page.content, 'html.parser')
	fullPage = soup.get_text();

	# ident table start
	tableLoc = fullPage.find('Top 10 Holdings')
	if(tableLoc == -1):
		tableLoc = fullPage.find('Top 25 Holdings')

	reducedStr = fullPage[tableLoc:]

	#Remove space
	str = re.sub(r'\n\s*\n', '\n', reducedStr, flags=re.MULTILINE)

	return str

# Main
def getHoldings(filename, month, year):
	symbols = interestingFunds()
	#symbols = ["FFGIX", "FFGCX", "FSRRX", "FACNX", "FIQJX", "FCSRX", "FSMEX", "FGKPX", "VTIVX"]

	symbols = sortSymbols(symbols)      # Sort symbols & remove duplicates

	URL = 'https://www.marketwatch.com/investing/fund/'
	URLLong = '/holdings'

	symbolsData = [] # prealloc container
	# top of the spreadsheet
	symbolsData.append(['Fund','Company Symbol','Total Net Assets','Total Net Assets','Monthly Rtn'])
	for symbol in symbols:
		print(symbol)
		URLSym = URL + symbol
		#URLSym += URLLong 		#Get top 25 instead of top 10
		
		page = requests.get(URLSym)
		pageProc = procRequest(page)
		holdings = " "
		holdings, asOf = buildHoldings(pageProc, month, year)
		
		strList = [symbol] + [asOf]
		symbolsData.append(strList)
		for i in holdings:
			symbolsData.append([" "] + i)
		
	seralizeData(filename, symbolsData)

if __name__ == "__main__":
    import sys

    year = None                        # month to lookup
    if(len(sys.argv) >= 4):
    	year = sys.argv[3]

    month = None                        # month to lookup
    if(len(sys.argv) >= 3):
    	month = sys.argv[2]

    filename = 'fundHoldings.xlsx'   # File name to seralize data
    if(len(sys.argv) >= 2):
    	filename = sys.argv[1]

    getHoldings(filename, month, year)
