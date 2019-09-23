"""Financial Calculator

This module implements a number of financial formulas used to value
stocks using financial statemements
"""

from financial import intrinio_data
import math
from exception.exceptions import CalculationError


def get_graham_number(ticker : str, year : int):
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


def get_historical_fcf(ticker: str, year_from: int, year_to: int):
    """
        retuns a historical list of historical free cashflows given
        a ticker, start and end year.

        Note that the FCF is an estimate computed as

        FCF = Operating Income - CAPEX

        Parameters
        ----------
        ticker : str
        Ticker Symbol
        year_from : int
        Start year of the FCF list
        year_to : int
        End year of the FCF list 

        Returns
        -------
        A dictionary of year=>FCF value. For example

        {
            2010: 16590000000.0,
            2011: 33269000000.0
        }
    """
    fcf_dict = {}

    # tags required by for estimate fcf calculation
    fcf_tag_filter = [
        'netcashfromcontinuingoperatingactivities',
        'purchaseofplantpropertyandequipment'
    ]

    cashflow_statements = intrinio_data.get_historical_cashflow_stmt(
        ticker, year_from, year_to, fcf_tag_filter)

    for year, cashflow in sorted(cashflow_statements.items()):
        fcf = cashflow['netcashfromcontinuingoperatingactivities'] + \
            cashflow['purchaseofplantpropertyandequipment']
        fcf_dict[year] = fcf

    return fcf_dict
