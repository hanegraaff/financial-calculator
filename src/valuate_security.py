"""valuate_security.py

"""
import argparse
import datetime
from datetime import timedelta
import logging
from support import util
from exception.exceptions import BaseError
from financial import calculator
from data_provider import intrinio_data
from dcf_models.jimmy_model import JimmyDCFModel
from reporting.spreadsheet_report import init_report_dir
from support.financial_cache import cache

#
# Main script
#

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')

description = """ Performs a DCF analisys of a stock and returns the intrinsic price.

                  The parameters are a ticker symbol (or file containing one symbol per line)
                     and a year represending the most recent available year end reports. The year
                     also represents the date of the intrinsic price. So for example, if the
                     supplied parameters are "AAPL" and "2018", then the output will be the
                     price for AAPL during Q4 2018.
              """



parser = argparse.ArgumentParser(description=description)
parser.add_argument("-ticker", help="Ticker Symbol", type=str)
parser.add_argument("-ticker-file", help="Ticker Symbol file", type=str)
parser.add_argument("year", help="Year of the most recent year end financial statements", type=int)

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

today = datetime.datetime.now()
five_days_ago = today - timedelta(days=5)

ticker_list = []

if (ticker != None):
    ticker_list.append(ticker)
else:
    try:
      with open(ticker_file) as f:
        ticker_list = f.read().splitlines()
    except Exception as e:
        logging.error("Could run script, because, %s" % (str(e)) )
        exit(-1)

init_report_dir()

for ticker in ticker_list:

  try:

    price_dict = intrinio_data.get_daily_stock_close_prices(ticker, five_days_ago, today)
    
    latest_price = price_dict[sorted(list(price_dict.keys()), reverse=True)[0]]
    
    dcf_model = JimmyDCFModel(ticker, year)
    dcf_price = dcf_model.calculate_dcf_price()
    
    log.info("Tiker: %s, Intrinsic Price: %.6f, Current Price: %.6f" % (ticker, dcf_price, latest_price))
    log.debug(util.format_dict(dcf_model.get_itermediate_results()))

    dcf_model.generate_report()

  except BaseError as be:
    print("Could not valuate %s, %d because: %s" % (ticker, year, str(be)))

# close the financial cache
cache.close()