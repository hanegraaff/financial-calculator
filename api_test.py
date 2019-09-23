from __future__ import print_function
import time
import intrinio_sdk
from intrinio_sdk.rest import ApiException
from pprint import pprint
import os

API_KEY = os.environ['INTRINIO_API_KEY']

intrinio_sdk.ApiClient().configuration.api_key['api_key'] = API_KEY

'''company_api = intrinio_sdk.CompanyApi()

identifier = 'AAPL' # str | A Company identifier (Ticker, CIK, LEI, Intrinio ID)
filed_after = '' # date | Filed on or after this date (optional)
filed_before = '' # date | Filed on or before this date (optional)
reported_only = False # bool | Only as-reported fundamentals (optional)
fiscal_year = "2018" # int | Only for the given fiscal year (optional)
statement_code = '' # str | Only of the given statement code (optional)
type = '' # str | Only of the given type (optional)
start_date = '' # date | Only on or after the given date (optional)
end_date = '' # date | Only on or before the given date (optional)
page_size = 100 # int | The number of results to return (optional) (default to 100)
next_page = '' # str | Gets the next page of data from a previous API call (optional)

try:
  api_response = company_api.get_company_fundamentals(identifier, filed_after=filed_after, filed_before=filed_before, reported_only=reported_only, fiscal_year=fiscal_year, statement_code=statement_code, type=type, start_date=start_date, end_date=end_date, page_size=page_size, next_page=next_page)
  pprint(api_response)
except ApiException as e:
  print("Exception when calling CompanyApi->get_company_fundamentals: %s\r\n" % e)'''

company_api = intrinio_sdk.CompanyApi()

identifier = 'AAPL' # str | A Company identifier (Ticker, CIK, LEI, Intrinio ID)
#tag = 'marketcap' # str | An Intrinio data tag ID or code reference [see - https://data.intrinio.com/data-tags]
tag = 'bookvaluepershare' # str | An Intrinio data tag ID or code reference [see - https://data.intrinio.com/data-tags]
frequency = 'quarterly' # str | Return historical data in the given frequency (optional) (default to daily)
typ = 'TTM' # str | Return historical data for given fiscal period type (optional)
start_date = '2010-01-01' # date | Return historical data on or after this date (optional)
end_date = '' # date | Return historical data on or before this date (optional)
sort_order = 'desc' # str | Sort by date `asc` or `desc` (optional) (default to desc)
page_size = 100 # int | The number of results to return (optional) (default to 100)
next_page = '' # str | Gets the next page of data from a previous API call (optional)

try:
  api_response = company_api.get_company_historical_data(identifier, tag, frequency=frequency, type=typ, start_date=start_date, end_date=end_date, sort_order=sort_order, page_size=page_size, next_page=next_page)
  pprint(api_response)
except ApiException as e:
  print("Exception when calling CompanyApi->get_company_historical_data: %s\r\n" % e)