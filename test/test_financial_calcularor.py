import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from exception.exceptions import ValidationError
from exception.exceptions import DataError
from exception.exceptions import CalculationError
from financial import intrinio_data
from financial import calculator


class TestFinancialCalculator(unittest.TestCase):

    '''
        get_graham_number_test
    '''

    def test_get_graham_number_with_exception(self):
        with patch.object(intrinio_data.company_api, 'get_company_historical_data',
                          side_effect=ApiException("Not Found")):
            with self.assertRaises(DataError):
                calculator.get_graham_number(
                    'NON-EXISTENT-TICKER', 2018)

    def test_get_graham_number_with_invalid_year(self):
        with self.assertRaises(ValidationError):
            calculator.get_graham_number('AAPL', 0)

        with self.assertRaises(ValidationError):
            calculator.get_graham_number('AAPL', 0)

    def test_get_graham_number_with_negative_eps(self):
        with patch.object(intrinio_data, 'get_diluted_eps',
                          return_value=-1):
            with self.assertRaises(CalculationError):
                calculator.get_graham_number('AAPL', 2018)

    def test_get_graham_number_with_negative_bvps(self):
        with patch.object(intrinio_data, 'get_bookvalue_per_share',
                          return_value=-1):
            with self.assertRaises(CalculationError):
                calculator.get_graham_number('AAPL', 2018)
