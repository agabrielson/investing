# Investing Research Tools


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
	# monthlyMetrics.py: Collect monthly pricing data for funds of interest. Most pricing services provide limited granularity.
	# quartelyMetrics.py: Pull longer term data points together that can be extremely time consuming.
	# getHoldings.py: Extract fund holdings and attempt to get monthly return

Examples calls are located in the header of each python file mentioned above

## Approach

One way to use this capability...
1. Download data points available today with the scripts 
1. Bring the data points together into a larger spreadsheet to see longer term trends
1. Analyze the trends that interest you
1. You can decide which funds to inved in based on your strategy.
tracking has a sample spreadsheet used to track data points over multiple months

## Finding funds of interest

 Mutual funds are typically described somewhere in Edgar. If you search for a specific fund, you can find others grouped within an instition. Note a bank like Fidelity has many institions. Not all funds referenced in Edgar are current - funds may have shutdown.

 	```
	https://www.sec.gov/edgar/searchedgar/mutualsearch.html
	```

## License
Distributed under the MIT License. See LICENSE for more information.
