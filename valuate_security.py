"""valuate_security.py


"""
from financial import calculator
import argparse
import logging
from exception.exceptions import BaseError

#
# Main script
#

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] - %(message)s')

description = """ This financial calculator will generate various metrics
                  given a single ticker symbol or a file and a year.
            
                  Currently only support Graham Number calculation.

                  When processing metrics for multiple securities you may
                  supply a text file containing a list of securities, one per line.
                  
                  Parameters must include either -ticker or -ticker-file parameter"""



parser = argparse.ArgumentParser(description=description)
parser.add_argument("-ticker", help="Ticker Symbol", type=str)
parser.add_argument("-ticker-file", help="Ticker Symbol file", type=str)
parser.add_argument("year", help="Year", type=int)

log = logging.getLogger()



args = parser.parse_args()

ticker = args.ticker.upper() if args.ticker != None else None
ticker_file = args.ticker_file
year = args.year

if ((ticker == None and ticker_file == None) or (ticker != None and ticker_file != None)):
    print("Invalid Parameters. Must supply either 'ticker' or 'ticker-file' parameter")
    exit(-1)

log.debug("Parameters:")
log.debug("Ticker: %s" % ticker)
log.debug("Ticker File: %s" % ticker_file)
log.debug("Year: %d" % year)

calculator.calc_dcf_price(ticker, year)

log.info("Done")

'''ticker_list = []

if (ticker != None):
    ticker_list.append(ticker)
else:
    try:
      with open(ticker_file) as f:
        ticker_list = f.read().splitlines()
    except Exception as e:
        print("Could run script, because, %s" % (str(e)) )
        exit(-1)

for ticker in ticker_list:
  try:
    if ticker == "DWDP":
          x = 0
    graham_number = calculator.calc_graham_number(ticker, year)
    print("The graham number for %s, %d is: %2f" % (ticker, year, graham_number))
  except BaseError as be:
    print("Could not calculate graham number for %s, %d because: %s" % (ticker, year, str(be)))
'''



