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

import yfinance as yf
import pandas as pd
import requests
import re 
import numpy
from bs4 import BeautifulSoup
from datetime import date

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

# Deduplicate symbols and sort them
def sortSymbols(symbols):
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    return res

# Write data to the filesystem
def seralizeData(filename, dataList):
	df = pd.DataFrame(dataList)
	df.to_excel(filename)

# Main
def getHoldings(filename, month, year):
	symbols = ['FSAIX','FSCPX','FCYIX','FSDAX','FSDCX','FSELX','FSENX','FSESX','FSLEX','FIDSX','FDFAX',
            'FDAGX','FDBGX','FDCGX','FDTGX','FDIGX','FIJCX','FSAVX','FSAGX','FGDIX','FGDAX','FGDBX',
            'FGDCX','FGDTX','FIJDX','FSPHX','FSVLX','FSCGX','FSDPX','FMFAX','FMFBX','FMFCX','FMFTX',
            'FMFEX','FIJFX','FSPCX','FDLSX','FSHCX','FSMEX','FSLXX','FSRBX','FBMPX','FGJMX','FGKMX',
            'FGDMX','FGEMX','FGHMX','FSNGX','FNARX','FNINX','FSPFX','FPHAX','FSRPX','FSCSX','FSPTX',
            'FSTCX','FTUAX','FTUBX','FTUCX','FTUTX','FTUIX','FIJGX','FBIOX','FSRFX','FSUTX','FWRLX',
            'FSLBX','FBSOX','FSCHX','FDCPX','FSHOX','FIUIX','FRESX','FIRAX','FIRBX','FIRCX','FIRTX',
            'FIREX','FIRIX','FIKLX','FFERX','FBIDX','FSEVX','FSEMX','FSMAX','FIBAX','FIBIX','FSIVX',
            'FSIIX','FSPNX','FSPSX','FLBAX','FLBIX','FSBAX','FSBIX','FSTVX','FSTMX','FFSMX','FSKTX',
            'FSKAX','FUSVX','FUSEX','FXSIX','FXAIX','FCHSX','FJPDX','FATJX','FMRMX','FIJVX','FARNX',
            'FLCSX','FMCSX','FKMCX','FNCMX','FOHIX','FOHJX','FJACX','FJAKX','FSLCX','FSCRX','FDFIX',
            'FFCLX','FCLKX','FKICX','FHLFX','FZIPX','FNILX','FZILX','FZROX','FIFNX','FIFWX','FIFOX',
            'FIFQX','FIFPX','FIFVX','FCFMX','FVCIX','FNKFX','FNIAX','FNIBX','FNICX','FNITX','FINSX',
            'FZANX','FNIMX','FCNTX','FCNKX','FVWSX','FWWEX','FAMGX','FFPIX','FLCNX','FINPX','FIPAX',
            'FBIPX','FIPCX','FIPTX','FIPIX','FBNDX','FGBAX','FGBBX','FGBCX','FGBTX','FGBPX','FIKQX',
            'FHIFX','SPHIX','FSHBX','FSBFX','FBNAX','FBNTX','FANCX','FBNIX','FIKTX','SPGVX','FTHRX',
            'FSRRX','FSRAX','FSBRX','FCSRX','FSRTX','FSIRX','FRRFX','FIQDX','FSRKX','FBIDX','FUBFX',
            'FSITX','FXSTX','FXNAX','FIBIX','FIBAX','FUPDX','FUAMX','FLBAX','FLBIX','FNAMX','FNBGX',
            'FSBAX','FSBIX','FBENX','FUMBX','FTABX','FSDIX','FASDX','FBSDX','FCSDX','FTSDX','FSIDX',
            'FSDTX','FIQWX','FSLXX','FDYSX','FDASX','FDBSX','FDCSX','FDTSX','FDYIX','FSIGX','FIBFX',
            'FFCSX','FCSSX','FCSFX','FSGEX','FSIPX','FFIPX','FCBFX','FCBAX','FCCCX','FCBTX','FCBIX',
            'FIKOX','FCONX','FCNVX','FMLCX','FAMPX','FAMIX','FAVIX','FMIFX','FAMMX','FACIX','FMCFX',
            'FAPAX','FOMIX','FOCFX','FOMAX','FPMAX','FPADX','FPMIX','FPEMX','FSGDX','FSGGX','FSGSX',
            'FSGUX','FSMDX','FSTPX','FSCLX','FSCKX','FSSVX','FSSNX','FSSSX','FSSPX','FSRVX','FSRNX',
            'FRXIX','FSIQX','FSIYX','FIPBX','FIPDX','FCHPX','FSODX','FSWTX','FIOOX','FSIOX','FYBTX',
            'FYCTX','FYATX','FSUVX','FSKLX','FZFLX','FUQIX','FBLTX','FESIX','FLCPX','FERGX','FIONX',
            'FUTBX','FGNXX','FFGXX','FSUIX','FSUPX','FSWIX','FSPGX','FLCHX','FLCDX','FLCMX','FLCOX',
            'FTIUX','FTIPX','FTIGX','FTIHX','FTLTX','FFTTX','FUMIX','FBUIX','FIBUX','FITFX','FLAPX',
            'FLXRX','FBSTX','FUSTX','FLXSX','FNIDX','FNIYX','FNIRX','FITLX','FENSX','FPNSX','FIMSX',
            'FAMHX','FAMYX','FNSJX','FNSKX','FNSOX','FNSLX','FIWCX','FSWCX','FMQXX','FNDSX','FNASX',
            'FNBSX','FJTDX','FSMNX','FSAJX','FSMTX','FHMFX','FHOFX','FGKPX','FIFZX','FMBIX','FSABX',
            'FMDGX','FIMVX','FECGX','FISVX','FBIIX','FEMVX','FITMX','FQITX','FZOLX','FZOMX','FBALX',
            'FBAKX','FLPSX','FLPKX','FPURX','FPUKX','FVDFX','FVDKX','FDMLX','FGLLX','FFNPX','FLKSX',
            'FDVKX','FBKFX','FPKFX','FGVAX','FGVBX','FGECX','FGVTX','FRVIX','FOCPX','FOCKX','FRIFX',
            'FRINX','FRIOX','FRIQX','FRIRX','FIKMX','FCPGX','FCAGX','FCBGX','FCCGX','FCTGX','FCIGX',
            'FCPFX','FIDGX','FSTOX','FCPVX','FCVAX','FCVBX','FCVCX','FCVTX','FCVIX','FSVFX','FIKNX',
            'FBGRX','FBGKX','FBCFX','FBCVX','FDGFX','FDGKX','FGRIX','FGIKX','FIREX','FIRAX','FIRBX',
            'FIRCX','FIRTX','FIRIX','FLVCX','FLCKX','FSOPX','FSOFX','FSREX','FSRWX','FREDX','FREFX',
            'FSBDX','FSBEX','FLCLX','FBCGX','FOCSX','FOKFX','FTRNX','FEMKX','FDSCX','FIGRX','FAIDX',
            'FADDX','FCADX','FTADX','FIADX','FIDKX','FZAIX','FIEUX','FEUFX','FHJUX','FHJWX','FHJTX',
            'FHJVX','FHJMX','FIQHX','FGBLX','FJPNX','FJPFX','FPJAX','FJPBX','FJPCX','FJPTX','FJPIX',
            'FIQLX','FJSCX','FLATX','FLFAX','FLFBX','FLFCX','FLFTX','FLFIX','FIQMX','FNORX','FOSFX',
            'FOSKX','FFOSX','FPBFX','FSEAX','FSEFX','FWWFX','FWAFX','FWBFX','FWCFX','FWTFX','FWIFX',
            'FIQOX','FISMX','FIASX','FIBSX','FICSX','FTISX','FIXIX','FIQIX','FSCOX','FOPAX','FOPBX',
            'FOPCX','FOPTX','FOPIX','FIQJX','FIVFX','FICDX','FACNX','FBCNX','FCCNX','FTCNX','FICCX',
            'FIQEX','FHKCX','FHKAX','FHKBX','FCHKX','FHKTX','FHKIX','FIQFX','FDIVX','FDIKX','FDVFX',
            'FEMKX','FKEMX','FEQMX','FZEMX','FEDMX','FEMMX','FECMX','FECAX','FIVLX','FIVMX','FIVNX',
            'FIVOX','FIVPX','FIVQX','FIQKX','FIGFX','FIAGX','FBIGX','FIGCX','FITGX','FIIIX','FZAJX',
            'FTCEX','FTTEX','FTEIX','FTIEX','FTAEX','FTBEX','FIEZX','FEMEX','FMEAX','FEMBX','FEMCX',
            'FEMTX','FIEMX','FEMSX','FEMFX','FFGCX','FFGAX','FFGBX','FCGCX','FFGTX','FFGIX','FIQRX',
            'FIGSX','FFIGX','FINVX','FFVNX','FSTSX','FFSTX','FEDDX','FEDAX','FEDGX','FEDTX','FEDIX',
            'FIQGX','FTEJX','FTEMX','FTEDX','FTEFX','FTEHX','FIQNX','FGILX','FULTX','FKIDX','FAPCX',
            'FCNSX','FHKFX','FISZX','FDKFX','FSOSX','FNSTX','FEOPX','AWTAX','VTIVX','BFOCX']
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
			try:
				symbolsData.append([" "] + i)
			except:
				print("getHoldings: Error")
		
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