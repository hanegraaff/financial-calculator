import datetime
import intrinio_sdk
from intrinio_sdk.rest import ApiException
import os

"""
This module is a value add to the Intrinion SDK
and implements a number of functions to read current and historical
financial statements
"""

API_KEY = os.environ['INTRINIO_API_KEY']

intrinio_sdk.ApiClient().configuration.api_key['api_key'] = API_KEY
fundamentals_api = intrinio_sdk.FundamentalsApi()


def get_historical_cashflow_stmt(ticker : str, year_from : int, 
  year_to : int, tag_filter_list : list):

  """
    returns a partial or complete seto of cashflow statements given
    a ticker symbol, year from, year to and a list of tag filters
    used to narrow the results.

    Parameters
    ----------
    ticker : str
      Ticker Symbol
    year_from : int
      Start year of financial statement list
    year_to : int
      End year of the financial statement list 
    tag_filter_list : list
      List of data tags used to filter results. The name of each tag
      must match an expected one from the Intrinio API
    
    Returns
    -------
    A dictionary of year=>dict with the filtered results. For example:

    {2010: {
      'netcashfromcontinuingoperatingactivities': 77434000000.0,
      'purchaseofplantpropertyandequipment': -13313000000
    },}

  """

  # return value
  hist_statements = {}
  ticker = ticker.upper()

  try:
    for i in range(year_from, year_to + 1):
      satement_name = ticker + "-cash_flow_statement-" + str(i) + "-FY"
    
      cashflow_statement = fundamentals_api.get_fundamental_standardized_financials(satement_name)
      
      filtered_financials = __get_from_financial_stmt__(cashflow_statement.standardized_financials, tag_filter_list)

      hist_statements[i] = filtered_financials

  except ApiException as e:
    #todo rethrow a different exception
    print("Exception when reading cashflow statement APIs: %s" % e)
    return {}

  return hist_statements
    
def __get_from_financial_stmt__(std_financials_list : list, tag_filter_list : list): 
  """
    Helper function that returns specific financials from a statement
    given a list of Intrinio tags. 
    
    For example we could extract "operating cashflow"
    and "capex" from the cash flow statement.

    Parameters
    ----------
    std_financials_list : list
      List of standardized financials extracted from the 
    tag_filter_list : list
      List of data tags used to filter results. The name of each tag
      must match an expected one from the Intrinio API
    
    Returns
    -------
    A dictionary of tag=>value with the filtered results. For example:

    {
      'netcashfromcontinuingoperatingactivities': 77434000000.0,
      'purchaseofplantpropertyandequipment': -13313000000
    }

    Note that the name of the tags are specific to the Intrinio API
  """
  results = {}

  for financial in std_financials_list:

    if (tag_filter_list == None or
        financial.data_tag.tag in tag_filter_list):
      results[financial.data_tag.tag] = financial.value

  return results
