#!/usr/bin/env python
# coding: utf-8

# monthlyMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#   month:      month to collect data points for, can be left blank
#   year:       year to collect data points for, can be left blank
#
# Examples
#   python3 monthlyMetrics.py               -> outputs in interestSymbols.xlsx
#   python3 monthlyMetrics.py data.xlsx     -> outputs in data.xlsx
#       Notes: Run after the first business day of the month
#   python3 monthlyMetrics.py march.xlsx 3
#       Notes: Collect data for March of this year, outputs in march.xlsx 
#   python3 monthlyMetrics.py dec2020.xlsx 12 2020
#
# Rev History:
#   0.1     210303      Initial Functionality
#   0.2     210403      Added previous month lookup
#   0.21    210403      Cleaned up code flow for one path
#   0.25    210405      Added year
#   0.26    210410      Adding significantly more symbols

import yfinance as yf
import pandas as pd
from datetime import date

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

def endMonthYear(month, year):
    month, year = startMonthYear(month, year)
    month = month + 1
    if month == 13:
        month = 1
        year = year + 1

    return month, year;

def getMetrics(symbol, month, year):
    month, year = startMonthYear(month, year)
    monthEnd, yearEnd = endMonthYear(month, year)

    start = "%4.4d-%2.2d-%2.2d" % (year, month, 1)
    end = "%4.4d-%2.2d-%2.2d" % (yearEnd, monthEnd, 1)
    symDaily = yf.download(symbol, start, end, interval="1m")

    #print(symDaily)
    dayFirst = symDaily.iloc[0].Close
    dayEnd = symDaily.iloc[-1].Close

    dataList = [symbol, dayFirst, dayEnd, dayEnd/dayFirst]    
    return dataList

def sortSymbols(symbols):
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    symbols = res
    return symbols

def seralizeData(filename, dataList):
    df = pd.DataFrame (dataList,columns=['Symbol', 'Month Start', 'Month End', 'PERC'])
    #df = df.T
    #print(df)
    df.to_excel(filename)

def monthlyMetric(filename, month, year):
    # Define symbols of interest
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
            'FCNSX','FHKFX','FISZX','FDKFX','FSOSX','FNSTX','FEOPX','FDCAX','FCAKX','FDEQX','FDEKX',
            'FDEFX','FTQGX','FDSCX','FCDAX','FCDBX','FCDCX','FCDTX','FCDIX','FSSZX','FDSSX','FSSKX',
            'FMAMX','FHRLX','FLACX','FSJHX','FBRNX','FZAPX','FDVLX','FVLKX','FCUTX','FDSVX','FGDKX',
            'FFTYX','FFIDX','FFDKX','FGRTX','FGTAX','FGRBX','FGRCX','FTGRX','FTRIX','FZALX','FEDCX',
            'FEDFX','FGLGX','FTBTX','FMALX','FSEDX','FLGEX','FLVEX','FLCEX','FIENX','FMEIX','FCPEX',
            'FVSAX','AWTAX','VTIVX','BFOCX']
    #symbols = ['FSMEX']
    
    symbols = sortSymbols(symbols)      # Sort symbols & remove duplicates

    dataList = []                       # Allocate variable name
    for symbol in symbols:              # Lookup symbols
        try:
            dataList.append(getMetrics(symbol, month, year))
        except:
            dataList.append([symbol])

    seralizeData(filename, dataList)    # Seralize data

if __name__ == "__main__":
    import sys
    
    year = None                        # month to lookup
    if(len(sys.argv) >= 4):
        year = sys.argv[3]

    month = None                        # month to lookup
    if(len(sys.argv) >= 3):
        month = sys.argv[2]

    filename = 'interestSymbols.xlsx'   # File name to seralize data
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

    monthlyMetric(filename, month, year)      # run monthMetrics to collect data
