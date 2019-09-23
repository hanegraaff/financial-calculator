import datetime
import intrinio_sdk
from intrinio_sdk.rest import ApiException
import os
import math
from exception.exceptions import DataError, ValidationError
from financial import util

"""
This module is a value add to the Intrinion SDK
and implements a number of functions to read current and historical
financial statements
"""

API_KEY = os.environ['INTRINIO_API_KEY']

intrinio_sdk.ApiClient().configuration.api_key['api_key'] = API_KEY

fundamentals_api = intrinio_sdk.FundamentalsApi()
data_point_api = intrinio_sdk.DataPointApi()
company_api = intrinio_sdk.CompanyApi()


def get_diluted_eps(ticker: str, year: int):
    '''
      Returns Intrinio's adjdilutedeps metric for the given year.
      This value is calcualted the same way as:

        This is the description from Intrinio documentation:

        Diluted EPS is a performance metric used to gauge the quality of a company's
        earnings per share (EPS) if all convertible securities were exercised.
        Convertible securities are all outstanding convertible preferred shares,
        convertible debentures, stock options (primarily employee-based) and warrants.
        Adjusted for stock splits.

      Parameters
      ----------
      ticker : str
        Ticker Symbol
      year : int
        Current or hisorical year to look up

      Returns
      -----------
      A number representing the diluted eps
    '''
    return __read_financial_metric__(ticker, year, 'adjdilutedeps')


def get_bookvalue_per_share(ticker: str, year: int):
    '''
      Returns Intrinio's bookvaluepershare metric for the given year.
      This value is calcualted the same way as:

        totalequity/weightedavedilutedsharesos

        from the income statement.

      Parameters
      ----------
      ticker : str
        Ticker Symbol
      year : int
        Current or hisorical year to look up

      Returns
      -----------
      A number representing the diluted eps
    '''

    return __read_financial_metric__(ticker, year, 'bookvaluepershare')


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

    hist_income_statements = __read_historical_financial_statement__(
        ticker, 'income_statement', year_from, year_to)

    for year, income_statement in hist_income_statements.items():
        filtered_income_statements[year] = __filter_financial_stmt__(
            income_statement, tag_filter_list)

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

    hist_balance_sheets = __read_historical_financial_statement__(
        ticker, 'balance_sheet_statement', year_from, year_to)

    for year, balace_sheet in hist_balance_sheets.items():
        filtered_balance_sheets[year] = __filter_financial_stmt__(
            balace_sheet, tag_filter_list)

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

    hist_casflow_statements = __read_historical_financial_statement__(
        ticker, 'cash_flow_statement', year_from, year_to)

    for year, cashflow_statement in hist_casflow_statements.items():
        filtered_casflows[year] = __filter_financial_stmt__(
            cashflow_statement, tag_filter_list)

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
            satement_name = ticker + "-" + \
                statement_name + "-" + str(i) + "-Q3"

            statement = fundamentals_api.get_fundamental_standardized_financials(
                satement_name)

            hist_statements[i] = statement.standardized_financials

    except ApiException as e:
        # todo rethrow a different exception
        print("Exception when reading %s statement APIs: %s" %
              (statement_name, e))
        return {}

    return hist_statements


def __read_financial_metric__(ticker: str, year: int, tag: str):

    (start_date, end_date) = util.get_fiscal_year_period(year, 0)
    frequency = 'yearly'

    try:
        api_response = company_api.get_company_historical_data(
            ticker, tag, frequency=frequency, start_date=start_date, end_date=end_date)
    except ApiException as ae:
        raise DataError(
            "Error retrieving ('%s', %d) -> '%s' from Intrinion API" % (ticker, year, tag), ae)
    except Exception as e:
        raise ValidationError(
            "Error parsing ('%s', %d) -> '%s' from Intrinion API" % (ticker, year, tag), e)

    if len(api_response.historical_data) == 0:
        raise DataError("No Data returned for ('%s', %d) -> '%s' from Intrinion API" % (ticker, year, tag), None)

    return api_response.historical_data[0].value


def __read_current_financial_metric__(ticker: str, tag: str):
    try:
        return data_point_api.get_data_point_number(ticker, tag)
    except ApiException as e:
        raise
