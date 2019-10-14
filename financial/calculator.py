"""Financial Calculator

This module implements a number of financial formulas used to value
stocks using financial statemements
"""

from financial import intrinio_data
import math
from exception.exceptions import CalculationError, DataError
import logging
from log import util

log = logging.getLogger()

def calc_dcf_price(ticker, year):
    """
        Computes a rough DCF calculation based on the "Jimmy" method, which
        is based this video:

        https://www.youtube.com/watch?v=fd_emLLzJnk&t=500s

        These are the steps
        -------------------
        1) Generate 4 years of historical free cash flow to equity (y-4, y)
        2) Generate 4 years of historical net income
        3) Determine the FCFE / net income for both sets and pick the most
           conservative number. Alternatively it could be an average of all
           numbers.
        4) Generate 4 years of historical revenue. Determine average growth, and
           and Forecast the next 4 years. The video suggests using two years of
           analyst forecast. Here we use the historical average.
        5) Determine historical profit margin (net margin) by dividing net income
           by revenue. Ideally the profit margin shoul be fairly consistent.
        6) Forecast net income by multipling revenue by margin
        7) Forecast FCFE by multiplying net income by the number determined in step 3.



        Parameters
        ----------
        ticker : str
        Ticker Symbol
        year : int
        The current or historical to use for valuation

        Returns
        -------
        the Price per share based on the calculation
    """

    start_year = year - 4
    end_year = year

    def __calc_fcfe_ni_ratio__(hist_fcfe : dict, hist_net_income : dict):
        """
            calculates the ratio of fcfe to net income ratio and return
            the most conservative (smallest) value
        """

        fcfe_ni_ratio = {}

        for i in range(start_year, end_year + 1):
            fcfe_ni_ratio[i] = hist_fcfe[i] / hist_net_income[i]

        log.debug("Historical fcfe/ni ratio: %s" % util.format_dict(fcfe_ni_ratio))
        return sorted(fcfe_ni_ratio.values())[0]
    
    def __forecast_revenue_growth__(hist_revenue :  dict):
        return 0
    
    '''log.info("Computing DCF for: %s, %d" % (ticker, year))

    cashflow_statements = intrinio_data.get_historical_cashflow_stmt(
        ticker, start_year, end_year, None)

    # get historical fcfe
    historical_fcfe = get_historical_simple_fcfe(cashflow_statements)
    logging.debug("Historical FCFE: %s" % util.format_dict(historical_fcfe))


    # get historical net income
    historical_net_income = get_historical_net_income(cashflow_statements)
    logging.debug("Historical Net Income: %s" % util.format_dict(historical_net_income))

    # get fcfe_ni_ratio
    fcfe_ni_ratio = __calc_fcfe_ni_ratio__(historical_fcfe, historical_net_income)
    logging.debug("chosen fcfe/ni ratio: %3.6f" % fcfe_ni_ratio)

    # get historical revenue growth and determine growth rate
    historical_revenue = intrinio_data.get_historical_revenue(
        ticker, start_year, end_year)

    logging.debug("Total Revenue: %s" % util.format_dict(historical_revenue))
    revenue_growth = __forecast_revenue_growth__(historical_revenue)
    logging.info("Revenue Growth: %3.6f" % revenue_growth)'''


def calc_graham_number(ticker : str, year : int):
    """
        Returns the Graham number given a ticker symbol and a year.
        The year will be used to select the appropriate 10k reports that contain the
        required inputs.

        Parameters
        ----------
        ticker : str
        Ticker Symbol
        year : int
        The current or historical year of the Graham number. Must match the year
        of an existing 10k report.

        Returns
        -------
        The Graham number for the supplied ticker symbol and year
    """
    eps = intrinio_data.get_diluted_eps(ticker, year)
    book_value_per_share = intrinio_data.get_bookvalue_per_share(ticker, year)

    if eps <= 0:
        raise CalculationError("EPS value [%d] is invalid" % eps, None)

    if book_value_per_share <= 0:
        raise CalculationError("Book Value Share per value [%d] is invalid" % book_value_per_share, None)

    graham_number = math.sqrt(
        15 * 1.5 * (eps * book_value_per_share))

    return graham_number


def get_historical_net_income(cashflow_statements : dict):
    """
        Extracts the historical net income from the supplied cashflow statements

        Parameters
        ----------
        cashflow_statements : dict
            a dictionary of cashflow statements keyed by year, as returned by
            intrinio_data.intrinio_data.get_historical_cashflow_stmt

        Returns
        -------
        A dictionary of year=>"Net Income" values. For example

        {
            2010: 16590000000.0,
            2011: 33269000000.0
        }
    """
    net_income_dict = {}

    if cashflow_statements == None:
        raise DataError("Could not compute historical net income, because of invalid input", None)


    try:
        for year, cashflow in sorted(cashflow_statements.items()):
            net_income_dict[year] = cashflow['netincome']
    except KeyError as ke:
        raise DataError("Could not compute historical net income, because item is missing from the cash flow statement", ke)

    return net_income_dict



def get_historical_simple_fcfe(cashflow_statements : dict):
    """
        retuns historical free cash flow to equity using a simple formula
        and based of values on the cashflow statement.

        Simple FCFE is an estimate computed as:

        FCF = Operating Income - CAPEX

        Parameters
        ----------
        cashflow_statements : dict
            a dictionary of cashflow statements keyed by year, as returned by
            intrinio_data.intrinio_data.get_historical_cashflow_stmt

        Returns
        -------
        A dictionary of year=>FCF values. For example

        {
            2010: 16590000000.0,
            2011: 33269000000.0
        }
    """
    fcf_dict = {}

    if cashflow_statements == None:
        raise DataError("Count not compute historical fcfe, because of invalid input", None)

    try:
        for year, cashflow in sorted(cashflow_statements.items()):
            fcf = cashflow['netcashfromcontinuingoperatingactivities'] + \
                cashflow['purchaseofplantpropertyandequipment']
            fcf_dict[year] = fcf
    except KeyError as ke:
        raise DataError("Count not compute historical fcfe, because of missing information in the cash flow statement", ke)

    return fcf_dict
