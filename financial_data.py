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
data_point_api = intrinio_sdk.DataPointApi()


def get_current_eps(ticker : str):
      
      #
      # Get average weighted shares
      #
      weighted_avg_shares = __read_current_financial_metric__(ticker,'adjweightedavebasicsharesos')
      diluted_eps =  __read_current_financial_metric__(ticker,'adjdilutedeps')
      #preferred_dividends = __read_current_financial_metric__(ticker,'preferred_dividends')
      
      print("weighted_avg_shares: ", weighted_avg_shares)
      print("diluted_eps: ", diluted_eps)
      #print("preferred_dividends: ", preferred_dividends)

      #
      # Determine NET Incocme from Income statements
      #
      income_statement_filter = None

      #TODO: figure out a way to get most currentn statement
      income_statements = get_historical_income_stmt(
        ticker, 2018, 2018, income_statement_filter)

      net_income = income_statements[2018]['netincome']
      print("net_income: ", net_income)


      print("Basic EPS: ", net_income/weighted_avg_shares)


def get_historical_income_stmt(ticker: str, year_from: int,
                                year_to: int, tag_filter_list: list):
    """
      returns a dictionary containing partial or complete income statements given
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
    filtered_income_statements = {}
    ticker = ticker.upper()

    hist_income_statements = __read_historical_financial_statement__(ticker, 'income_statement', year_from, year_to)

    for year, income_statement in hist_income_statements.items():
      filtered_income_statements[year] = __filter_financial_stmt__(income_statement, tag_filter_list)

    return filtered_income_statements

def get_historical_balance_sheet(ticker: str, year_from: int,
                                year_to: int, tag_filter_list: list):
    """
      returns a dictionary containing partial or complete balance sheets given
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
    filtered_balance_sheets = {}
    ticker = ticker.upper()

    hist_balance_sheets = __read_historical_financial_statement__(ticker, 'balance_sheet_statement', year_from, year_to)

    for year, balace_sheet in hist_balance_sheets.items():
      filtered_balance_sheets[year] = __filter_financial_stmt__(balace_sheet, tag_filter_list)

    return filtered_balance_sheets


def get_historical_cashflow_stmt(ticker: str, year_from: int,
                                 year_to: int, tag_filter_list: list):
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
    filtered_casflows = {}
    ticker = ticker.upper()

    hist_casflow_statements = __read_historical_financial_statement__(ticker, 'cash_flow_statement', year_from, year_to)

    for year, cashflow_statement in hist_casflow_statements.items():
      filtered_casflows[year] = __filter_financial_stmt__(cashflow_statement, tag_filter_list)

    return filtered_casflows


def __filter_financial_stmt__(std_financials_list: list, tag_filter_list: list):
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


def __read_historical_financial_statement__(ticker: str, statement_name: str, year_from: int, year_to: int):
    """
      Helper function that will read the Intrinio API for each year in the range and
      return the results a dictionary of {year: APIResponse}

      for example:

      {
        2010: {... APIResponse ...},
        2011: {... APIResponse ...},
      }
    """
    # return value
    hist_statements = {}
    ticker = ticker.upper()

    try:
        for i in range(year_from, year_to + 1):
            satement_name = ticker + "-"  + statement_name + "-" + str(i) + "-FY"

            statement = fundamentals_api.get_fundamental_standardized_financials(
                satement_name)

            hist_statements[i] = statement.standardized_financials

    except ApiException as e:
        # todo rethrow a different exception
        print("Exception when reading %s statement APIs: %s" % (statement_name, e))
        return {}

    return hist_statements

def __read_current_financial_metric__(ticker : str, tag : str):
  try:
    return data_point_api.get_data_point_number(ticker, tag)
  except ApiException as e:
    print("Exception when calling DataPointApi when reading metric: %s, %s" % (tag, e))
    return None
