import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from exception.exceptions import ValidationError
from exception.exceptions import DataError
import financial_data


class TestFinancialIntrinioData(unittest.TestCase):

    '''
        get_diluted_eps is used a test for the more generic __read_financial_metric__
        method
    '''

    def test_get_dilutedeps_with_api_exception(self):
        with patch.object(financial_data.company_api, 'get_company_historical_data',
                          side_effect=ApiException("Server Error")):
            with self.assertRaises(DataError):
                financial_data.get_diluted_eps('NON-EXISTENT-TICKER', 2018)

    def test_get_dilutedeps_with_invalid_year(self):
        with self.assertRaises(ValidationError):
            financial_data.get_diluted_eps('AAPL', 0)

        with self.assertRaises(ValidationError):
            financial_data.get_diluted_eps('AAPL', 0)
