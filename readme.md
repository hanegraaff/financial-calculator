# Overview

A financial calculator capable of determining the instrinsic value of a company by performing a discounted cashflow analysis.

This calculator requires access to financial statements and stock prices to 
perform its calculations. This data is provided by Intrinio, and you should sign up for an access to key before using this software. You may sign up for sandbox access which will give you data on roughly 30 securities.

## The model
The Discounted Cash Flow model is simple to implement and requires only 3 imputs: A cashflow forecast for 4-5 years in the future, a long term growth rate and a discount rate. Although the formula is straight forward, getting the inputs right is not, and so the current implementation takes a very simplistic approach to this.

1) Discount rate is hardcoded, to 9.75% and can be changed programmatically.
2) The long term growth rate is is also hardcoded and set to the 10 year TBILL rate or 1.75%
3) Cash flow forecast is based on a modified version of the "Jimmy" Method (https://www.youtube.com/watch?v=fd_emLLzJnk&t=500s), but it's essentially based on past history.

Over time, additional more sophisticated models will be made available.


## Prerequisites

### API Keys
An API Key for the Intrinio (https://www.intrinio.com) with access to the "US Fundamentals and Stock Prices" feeds

the API should be saved to the environment like so:

```export INTRINIO_API_KEY=[your API key]```

### Setting up your virtual environment
You may also run this in a virtual environment

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the script

The calculation can be done either for an individual stock or a file containing a list of them.

The file should contain a signle ticker per line. As an example, see ```ticker-list.txt```

```
python valuate_security.py -h
usage: valuate_security.py [-h] [-ticker TICKER] [-ticker-file TICKER_FILE]
                           year

Performs a DCF analisys of a stock and returns the intrinsic price. The
parameters are ticker symbol (or file containing one security per line) and a
year represending the most recent year end reports.

positional arguments:
  year                  Year of the most recent year end financial statements

optional arguments:
  -h, --help            show this help message and exit
  -ticker TICKER        Ticker Symbol
  -ticker-file TICKER_FILE
                        Ticker Symbol file

```

Examples:

```
python valuate_security.py -ticker-file ticker-list.txt 2018
python valuate_security.py -ticker aapl 2018
```

## Output

```
> python valuate_security.py aapl 2018

[INFO] - Tiker: AAPL, Intrinsic Price: 298.168730, Current Price: 236.410000
```

## Unit Tests
You may run all unit tests using this command:

```./test.sh```

This command will execute all unit tests and run the coverage report (using coverage.py)

```
>./test.sh
.........................
----------------------------------------------------------------------
Ran 25 tests in 0.241s

OK
Name                         Stmts   Miss  Cover
------------------------------------------------
dcf_models/__init__.py           0      0   100%
dcf_models/base_model.py        12      4    67%
dcf_models/jimmy_model.py      106     87    18%
exception/exceptions.py         21      3    86%
financial/__init__.py            0      0   100%
financial/calculator.py         63      2    97%
financial/intrinio_data.py      83     29    65%
financial/util.py               13      0   100%
log/__init__.py                  0      0   100%
log/util.py                      3      1    67%
run_tests.py                     8      0   100%
test/__init__.py                 0      0   100%
------------------------------------------------
TOTAL                          309    126    59%

```
