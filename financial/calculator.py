"""Author: Mark Hanegraaff -- 2019

This module contains a various calculations used to support the valuation
models provided by this software.

This module will likely be refactored over time
"""

from financial import intrinio_data
import math
import datetime
import statistics
from datetime import timedelta
from exception.exceptions import CalculationError, DataError
import logging
from log import util

log = logging.getLogger()


def calc_enterprise_value(fcfe_forecast : dict, long_term_growth_rate : float, discount_rate : float):
    """
        Calculates the enterprise value by performing a Discounted Cash Flow calculation
        using a dictionary of forecasted cash flows a pair of growth rates and a discount rate

    """
    def validate_parameters():
        if (fcfe_forecast == None or len(fcfe_forecast) == 0
            or long_term_growth_rate <= 0 
            or discount_rate <= 0):
            raise CalculationError("Could not perform discounted cash flow because the supplied parameters are invalid", None)
        
        if (long_term_growth_rate >= discount_rate):
            raise CalculationError("Could not perform discounted cash flow because long test growth rate exceeds discount rate", None)

    discounted_cashflows = {}
    exp = 1

    validate_parameters()

    # todo, see if we can avoid this sort.
    years = sorted(fcfe_forecast.keys())
    start_year = years[0]
    end_year = years[len(years) - 1]

    logging.debug("Calculating Enterprise Value using DCF Formula")
    logging.debug("Discount Rate: %3.6f" % discount_rate)
    logging.debug("Long Term Growth rate: %3.6f" % long_term_growth_rate)

    # compute short term enterprise value
    for year in range(start_year, end_year + 1):
        discounted_cashflows[year] =  fcfe_forecast[year] / ((1 + discount_rate) ** exp)
        exp += 1

    short_term_ev = sum(discounted_cashflows.values())
    logging.debug("Short Term EV: %.6f" % short_term_ev)
    
    terminal_value_start_fcf = discounted_cashflows[end_year]

    terminal_value = terminal_value_start_fcf / (discount_rate - long_term_growth_rate)
    logging.debug("Terminal Value: %.6f" % terminal_value)

    return short_term_ev + terminal_value



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
