# Investing Research Tools

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#About-The-Project">About The Project</a></li>
    <li><a href="#Prerequisites">Prerequisites</a></li>
    <li><a href="#Usage">Usage</a></li>
    <li><a href="#Approach">Approach</a></li>
    <li><a href="#Finding-Funds-of-Interest">Finding Funds of Interest</a></li>
    <li><a href="#License">License</a></li>
    <li><a href="#Disclaimer">Disclaimer</a></li>
  </ol>
</details>

## About The Project

This repo speeds up the investing data collection to enable more consistent research. Finding the time to keep long term investment research up to date can be difficult. These scripts enable the discipline to be consistent and speed up data point collection. I typically migrate these data points into a larger portfolio spreadsheet.

## Prerequisites

### Clone the repo
   ```sh
   git clone https://github.com/agabrielson/investing.git
   ```
### Install dependencies
   ```sh
   $ pip install -r Requirements.txt
   ```

## Usage

Runable python scripts:
* getAllMutualFunds.py: Get a list of existing mutual funds and descriptions, can be used to build the table needed for other fund scripts.
* monthlyMetrics.py: Collect monthly pricing data for funds of interest. Most pricing services provide limited granularity.
* quartelyMetrics.py: Pull longer term data points together that can be extremely time consuming.
* getHoldings.py: Extract fund holdings and attempt to get monthly return
* getStocks.py: Get monthly stock returns for all stocks (US market)
* stocksQuartely.py: Pull longer term stock data points together for all stocks (US market)
* getHolders.py: Get the top 10 list of holders for a company 

Examples calls are located in the header of each python file mentioned above

## Approach

One way to use this capability...
1. Download data points available today with the scripts 
1. Bring the data points together into a larger spreadsheet to see longer term trends
1. Analyze the trends that interest you
1. You can decide which funds to inved in based on your strategy.
tracking has a sample spreadsheet used to track data points over multiple months

## Finding Funds of Interest

 Mutual funds are typically described somewhere in Edgar. If you search for a specific fund, you can find others grouped within an instition. Note a bank like Fidelity has many institions. Not all funds referenced in Edgar are current - funds may have shutdown.
 	
    https://www.sec.gov/edgar/searchedgar/mutualsearch.html

CIK Lookup data
    https://www.sec.gov/Archives/edgar/cik-lookup-data.txt

Edgar CIKS (Stocks)
    https://www.sec.gov/files/company_tickers.json

This code appears to have all stocks:
    https://github.com/shilewenuw/get_all_tickers

Searching mutual funds
    https://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK=FXAIX

Best list of all mutual funds:
    https://www.marketwatch.com/tools/mutual-fund/list/A

## License
Distributed under the MIT License. See LICENSE for more information.

## Disclaimer 

This disclaimer informs readers that the views, thoughts, and opinions expressed in the text belong solely to the author, and not necessarily to the author's employer, organization, committee or other group or individual.

In fact, you should develop an investment strategy that works for you
