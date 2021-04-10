#!/usr/bin/env python
# coding: utf-8

# quartelyMetrics.py
#
# Inputs
#   filename:   spreadsheet to output data, can be left blank
#
# Examples
#   python3 quartelyMetrics.py              -> outputs in quarterlySymbols.xlsx
#   python3 quartelyMetrics.py data.xlsx    -> outputs in data.xlsx
#      
# Rev History:
#   0.1 - 210303
#           Initial Functionality
#           Yahoo ytdReturn appears mistaken at times
#           Would like to add Fund Manager
#   0.15 - 210410
#           Adding significantly more symbols

import yfinance as yf
import pandas as pd
import datetime as dt

# What should be added?
#   Fund Manager

def getDate():
    dateTimeList = []
    today = dt.date.today()
    dateTimeList.append(today)
    return dateTimeList[0]

def getQuarterlyMetrics(symbol):
    sym = yf.Ticker(symbol)
    
    dateToday = getDate()
    sName = sym.info['symbol']
    lName = sym.info['longName']
    
    sustain = '-'
    if(sym.sustainability is not None):
        sustain = sym.sustainability['Value'].to_dict()['peerGroup']
        
    mstar = sym.info['morningStarRiskRating']
    expRatio = round(sym.info['annualReportExpenseRatio'],2)
    ytdRtn = round(sym.info['ytdReturn'],2)
    
    beta3 = "-"
    if(sym.info["beta3Year"] is not None):
        beta3 = round(sym.info['beta3Year'],2)
    
    totAss = round(sym.info['totalAssets']/(1000000),0) 
    turn = round(sym.info['annualHoldingsTurnover'],2)
    
    dataList = [dateToday, sName, lName, sustain, mstar, expRatio, ytdRtn, beta3, totAss, turn]
   
    return dataList

def quarterlyMetric(filename):
    # Allocate data & define symbols of interest
    dataList = []
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

    # Sort symbols & remove duplicates
    symbols = sorted(symbols)
    res = [] 
    [res.append(symbol) for symbol in symbols if symbol not in res]
    symbols = res

    # lookup data
    dateToday = getDate()
    for symbol in symbols:
        print(symbol)
        try:
            dataList.append(getQuarterlyMetrics(symbol))
        except:
            dataList.append([dateToday, symbol])

    #Seralize data
    df = pd.DataFrame (dataList,columns=['Date', 'Symbol', 'Long Name', 'Peer Group', 'Morningstar',
                                        'Exp Ratio', 'YTD Return(?!)', 'beta3', 'Total Assets ($M)',
                                        'Turnover'])
    #print(df)
    df.to_excel(filename)

if __name__ == "__main__":
        import sys
        filename = 'quarterlySymbols.xlsx'
        if(len(sys.argv) == 2):
            filename = sys.argv[1]

        quarterlyMetric(filename)
