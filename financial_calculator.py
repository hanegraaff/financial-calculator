import financial_data

"""
This module implements a number of financial formulas used to value
stocks using financial statemements
"""


def get_current_graham_number(ticker: str):
    return financial_data.get_current_eps(ticker)


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

    cashflow_statements = financial_data.get_historical_cashflow_stmt(
        ticker, year_from, year_to, fcf_tag_filter)

    for year, cashflow in sorted(cashflow_statements.items()):
        fcf = cashflow['netcashfromcontinuingoperatingactivities'] + \
            cashflow['purchaseofplantpropertyandequipment']
        fcf_dict[year] = fcf

    return fcf_dict
