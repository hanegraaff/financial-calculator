"""Author: Mark Hanegraaff -- 2019

This module contains a various calculations used to support the valuation
models provided by this software.

This module will likely be refactored over time
"""

from data_provider import intrinio_data
import math
import datetime
import statistics
from datetime import timedelta
from exception.exceptions import CalculationError, DataError
import logging
from support import util

log = logging.getLogger()


def calc_enterprise_value(fcfe_forecast : dict, long_term_growth_rate : float, discount_rate : float):
    """
        Calculates the enterprise value by performing a Discounted Cash Flow calculation
        using a dictionary of forecasted cash flows a growth rate and a discount rate

        Returns a float consisting of the sum of discounted cash flows and terminal value

        Parameters
        ----------
        fcfe_forecast : dict
            A dictionary (year->value) for cashflow forecasts
        long_term_growth_rate : float
            The long term groth rate used by the terminal value
        discount_rate : float
            The discount rate

        Returns
        -------
        A tuple containing the enterprise value as a float and dictionary of intermediate
        results used to aid in testing.
    """
    intermediate_results = {}

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
    history_start_year = years[0]
    history_end_year = years[len(years) - 1]

    # compute short term enterprise value
    for year in range(history_start_year, history_end_year + 1):
        discounted_cashflows[year] =  fcfe_forecast[year] / ((1 + discount_rate) ** exp)
        exp += 1

    intermediate_results['discounted_cashflows'] = discounted_cashflows

    terminal_value_start_fcf = discounted_cashflows[history_end_year]

    terminal_value = terminal_value_start_fcf / (discount_rate - long_term_growth_rate)
    intermediate_results['terminal_value'] = terminal_value
    
    enterprise_value = sum(discounted_cashflows.values()) + terminal_value
    intermediate_results['enterprise_value'] = enterprise_value

    return (enterprise_value, intermediate_results)



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
        raise DataError("Could not compute historical fcfe, because of invalid input", None)

    try:
        for year, cashflow in sorted(cashflow_statements.items()):
            fcf = cashflow['netcashfromcontinuingoperatingactivities'] + \
                cashflow['purchaseofplantpropertyandequipment']
            fcf_dict[year] = fcf
    except KeyError as ke:
        raise DataError("Could not compute historical fcfe, because of missing information in the cash flow statement", ke)

    return fcf_dict
