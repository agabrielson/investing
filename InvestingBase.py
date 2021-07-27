#!/usr/bin/env python
# coding: utf-8

# InvestingBase.py
#
# Rev History:
#   0.1		210418		New file - cleaning up similar code
#	0.2		210426		Add procRequest & standardize
#	0.21	210426		Start checking procRequest for errors
#	0.35	210501		Add enhanced symbol input; updated symbols to pandas dataframe
#	0.36	210714		Add stripHTML (from getAllETFs.py)
#	0.37	210724		Moving mwGetName, mwProcData from quarterlyETFMetrics

from datetime import date
import time
import pandas as pd
import requests
import re 

from bs4 import BeautifulSoup

# Get json from a URL
# Return json structure
def procStocks(URLSym):
	page = requests.get(URLSym)
	return page.json()

# Extract the ticker symbol
def extractTicker(stocksJson):
	symList = []
	for key in stocksJson: 	
		symList.append(stocksJson[key].get('ticker'))

	return symList

#Strip HTML tags
def stripHTML(entry):
    # Remove remaining html tags
    strippedEntry = []
    if type(entry) is not str: 
        #print(entry)
        entry = ' '.join([str(elem) for elem in entry])

    for line in entry.splitlines(True):
        line = line.lstrip()
        if not (line.startswith('<')):
            strippedEntry.append(line.rstrip('\n'))

    strippedEntry[1] = strippedEntry[1][1:-1]

    return strippedEntry
    
# Make a request and start to reduce the string
#   We are only interested in the table with holdings information
#	Try a few times if a URL has an issue...
def procRequest(URLSym, iter = 5, reducedText = True, **kwargs):
	
	if(iter == 0):	# Website is having issues...
		return ' '

	fail = False
	try:
		page = requests.get(URLSym, **kwargs)
	except (ConnectionResetError):
		fail = True

	# If the webpage is having issues, try again...
	if(page.ok == False or fail == True):
		print("URL Failed... Trying again")
		#print(page)
		time.sleep(0.2)
		return procRequest(URLSym, iter-1, reducedText, **kwargs)

	soup = BeautifulSoup(page.content, 'html.parser')
	if(reducedText == True):
		fullPage = soup.get_text()
	else:
		fullPage = soup.prettify()

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
	symbols.sort_index()
	symbols.drop_duplicates()

# Write data to the filesystem
def seralizeData(filename, dataList, cols = None):
	df = pd.DataFrame(dataList, columns=cols)
	df.to_excel(filename)

# Read in the symbols of interest
# Maintaining a structure has become unwieldy... Reading in a simple spreadsheet is easier.
def readFunds(filename):
	symbols = pd.read_csv(filename, index_col=0, dtype={'Name': str}, header=None) 
	return symbols

# mwProcData: Extract values of interest from a scraped webpage
#   This function is a bit targetted for MarketWatch
# Inputs
#   fullPage: page to look through
#   searchStr: string to find
# Returns
#   Value right after the search string
def mwProcData(fullPage, searchStr):
    tableLoc = fullPage.find(searchStr)
    redPage = fullPage[tableLoc:]
    reduced = redPage.splitlines()

    if (len(reduced) == 1):
        return None

    return reduced[1]

# mwGetName: Determine if ETF is open and locate full name
# Inputs
#   fullPage: page to look through
# Returns
#   nameLong: Long name of ETF
#   closed: True if closed/False if open
def mwGetName(fullPage):
    closed = False

    fp = fullPage.splitlines()
    nameLong = fp[1]
    totStrStart = nameLong.find('|')+2
    nameLong = nameLong[totStrStart:]
    totStrEnd = nameLong.find('Overview')-1
    nameLong = nameLong[:totStrEnd]

    #if(fullPage.find('closed')):
    #	closed = True

    NAVDate = mwProcData(fullPage, 'NAV Date')
    if(NAVDate == 'N/A'):
        closed = True

    return nameLong, closed