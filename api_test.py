from __future__ import print_function
import time
import intrinio_sdk
from intrinio_sdk.rest import ApiException
from pprint import pprint
import os

API_KEY = os.environ['INTRINIO_API_KEY']

intrinio_sdk.ApiClient().configuration.api_key['api_key'] = API_KEY

data_point_api = intrinio_sdk.DataPointApi()

identifier = 'AAPL' # str | An identifier for an entity such as a Company, Security, Index, etc (Ticker, FIGI, ISIN, CUSIP, CIK, LEI, Intrinio ID)
tag = 'freecashflow' # str | An Intrinio data tag ID or code reference [see - https://data.intrinio.com/data-tags]

try:
  api_response = data_point_api.get_data_point_number(identifier, tag)
  pprint(api_response)
except ApiException as e:
  print("Exception when calling DataPointApi->get_data_point_number: %s\r\n" % e)
    

    