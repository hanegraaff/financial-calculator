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
                calculator.calc_graham_number(
                    'NON-EXISTENT-TICKER', 2018)

    def test_get_graham_number_with_invalid_year(self):
        with self.assertRaises(ValidationError):
            calculator.calc_graham_number('AAPL', 0)

        with self.assertRaises(ValidationError):
            calculator.calc_graham_number('AAPL', 0)

    def test_get_graham_number_with_negative_eps(self):
        with patch.object(intrinio_data, 'get_diluted_eps',
                          return_value=-1):
            with self.assertRaises(CalculationError):
                calculator.calc_graham_number('AAPL', 2018)

    def test_get_graham_number_with_negative_bvps(self):
        with patch.object(intrinio_data, 'get_bookvalue_per_share',
                          return_value=-1):
            with self.assertRaises(CalculationError):
                calculator.calc_graham_number('AAPL', 2018)

    '''
        Historical Free CashFlow to equity tests
    '''

    def test_get_historical_simple_fcfe_valid_input(self):
        cashflow_statement = {
            2018 : {
                'netcashfromcontinuingoperatingactivities' :  1,
                'purchaseofplantpropertyandequipment' : 2
            }
        }

        fcf_dict = calculator.get_historical_simple_fcfe(cashflow_statement)

        self.assertEqual(fcf_dict[2018], 3)

    def test_get_historical_simple_fcfe_invalid_input(self):
        cashflow_statement = {
            2018 : {
                'aaa' :  1,
                'bbb' : 2
            }
        }

        with self.assertRaises(DataError):
            calculator.get_historical_simple_fcfe(cashflow_statement)

    def test_get_historical_simple_fcfe_no_input(self):
        cashflow_statement = None

        with self.assertRaises(DataError):
            calculator.get_historical_simple_fcfe(cashflow_statement)

    '''
        Historical Net Income tests
    '''
    def test_get_historical_ni_valid_input(self):
        cashflow_statement = {
            2018 : {
                'netincome' :  999
            }
        }

        ni_dict = calculator.get_historical_net_income(cashflow_statement)

        self.assertEqual(ni_dict[2018], 999)

    def test_get_historical_invalid_input(self):
        cashflow_statement = {
            2018 : {
                'aaa' :  999,
            }
        }

        with self.assertRaises(DataError):
            calculator.get_historical_net_income(cashflow_statement)

    def test_get_historical_no_input(self):
        cashflow_statement = None

        with self.assertRaises(DataError):
            calculator.get_historical_net_income(cashflow_statement)

    '''
        DCF Calculation Tests
    '''

    def test_dcf_no_fcf(self):
        with self.assertRaises(CalculationError):
            calculator.calc_enterprise_value(None, 0.03, 0.0975)

    def test_dcf_zero_growthrate(self):
        with self.assertRaises(CalculationError):
            calculator.calc_enterprise_value('AAPS', 0, 0.0975)


    def test_dcf_zero_discountrate(self):
        with self.assertRaises(CalculationError):
            calculator.calc_enterprise_value({2008: 100}, 0.03, 0)

    def test_dcf_same_growth_discount(self):
        with self.assertRaises(CalculationError):
            #(100 / 2)^1 + (100/0)
            calculator.calc_enterprise_value({2008: 100}, 1, 1)

    def test_dcf_simple(self):
        #100 / (2)^1 + (50/0.5) = 150
        dcf_price = calculator.calc_enterprise_value({2008: 100}, 0.5, 1)
        self.assertEquals(dcf_price, 150)

    def test_dcf_simple(self):
        #100 / (2)^1 + 50 / (2)^2 + (100/0.5) = 87.5
        dcf_price = calculator.calc_enterprise_value({2008: 100, 2009: 100}, 0.5, 1)
        self.assertEqual(dcf_price, 125)

        

    

