# Investing Research Tools


## About this Project

Finding time to keep long term investment research up to date can be difficult. These scripts speed up collection of interesting data. I typically migrate these data points into a larger portfolio spreadsheet.

## Build With

	1. Tools run with Python3
	1. yfinance: download initial data of interest
	1. pandas: container to hold data before generating a spreadsheet

## Usage
	# monthlyMetrics.py: Collect monthly pricing data for funds of interest. Most pricing services provide limited granularity.
	# quartelyMetrics.py: Pull longer term data points together that can be extremely time consuming.

Examples are in each python file

tracking has a sample spreadsheet used to track data points over multiple months

Find all mutual funds grouped in an instition (not all referenced are valid):
https://www.sec.gov/edgar/searchedgar/mutualsearch.html

## License
Distributed under the MIT License. See LICENSE for more information.
