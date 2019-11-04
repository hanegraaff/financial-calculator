import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from exception.exceptions import ValidationError
from exception.exceptions import DataError
from data_provider import intrinio_data
import datetime


class TestDataProviderIntrinioData(unittest.TestCase):

    '''
        get_diluted_eps is used a test for the more generic __read_financial_metric__
        method
    '''

    def test_get_dilutedeps_with_api_exception(self):
        with patch.object(intrinio_data.company_api, 'get_company_historical_data',
                          side_effect=ApiException("Server Error")):
            with self.assertRaises(DataError):
                intrinio_data.get_diluted_eps('NON-EXISTENT-TICKER', 2018)

    def test_get_dilutedeps_with_invalid_year(self):
        with self.assertRaises(ValidationError):
            intrinio_data.get_diluted_eps('AAPL', 0)

        with self.assertRaises(ValidationError):
            intrinio_data.get_diluted_eps('AAPL', 0)

    '''
        Financial statement tests
    '''
    def test_historical_cashflow_stmt_with_api_exception(self):
        with patch.object(intrinio_data.fundamentals_api, 'get_fundamental_standardized_financials',
                          side_effect=ApiException("Not Found")):
            with self.assertRaises(DataError):
                intrinio_data.get_historical_cashflow_stmt('NON-EXISTENT-TICKER', 2018, 2018, None) 

    def test_historical_income_stmt_with_api_exception(self):
        with patch.object(intrinio_data.fundamentals_api, 'get_fundamental_standardized_financials',
                          side_effect=ApiException("Not Found")):
            with self.assertRaises(DataError):
                intrinio_data.get_historical_income_stmt('NON-EXISTENT-TICKER', 2018, 2018, None) 

    def test_historical_balacesheet_stmt_with_api_exception(self):
        with patch.object(intrinio_data.fundamentals_api, 'get_fundamental_standardized_financials',
                          side_effect=ApiException("Not Found")):
            with self.assertRaises(DataError):
                intrinio_data.get_historical_balance_sheet('NON-EXISTENT-TICKER', 2018, 2018, None) 

    '''
        Stock Price Tests
    '''
    def test_daily_stock_prices_with_api_exception(self):
        with patch.object(intrinio_data.security_api, 'get_security_stock_prices',
                        side_effect=ApiException("Not Found")):
            with self.assertRaises(DataError):
                intrinio_data.get_daily_stock_close_prices('NON-EXISTENT-TICKER', datetime.date(2018, 1, 1), datetime.date(2019, 1, 1)) 

    def test_daily_stock_prices_with_other_exception(self):
        with patch.object(intrinio_data.security_api, 'get_security_stock_prices',
                        side_effect=KeyError("xxx")):
            with self.assertRaises(ValidationError):
                intrinio_data.get_daily_stock_close_prices('NON-EXISTENT-TICKER', datetime.date(2018, 1, 1), datetime.date(2019, 1, 1)) 
