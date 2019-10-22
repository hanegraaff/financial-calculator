import unittest
from exception.exceptions import ValidationError, CalculationError
from dcf_models.jimmy_model import JimmyDCFModel
from financial import intrinio_data
from unittest.mock import patch


class TestJimmyModel(unittest.TestCase):

    def test_dcf_no_symbol(self):
        with self.assertRaises(ValidationError):
            dcf_model = JimmyDCFModel(None, 2018)
            dcf_model.calculate_dcf_price()

    def test_dcf_simple(self):

        cashflow_statement = {
            2014: {
                'netcashfromcontinuingoperatingactivities': 10,
                'purchaseofplantpropertyandequipment': 10,
                'netincome': 10
            },
            2015: {
                'netcashfromcontinuingoperatingactivities': 20,
                'purchaseofplantpropertyandequipment': 20,
                'netincome': 20
            },
            2016: {
                'netcashfromcontinuingoperatingactivities': 30,
                'purchaseofplantpropertyandequipment': 30,
                'netincome': 30
            },
            2017: {
                'netcashfromcontinuingoperatingactivities': 40,
                'purchaseofplantpropertyandequipment': 40,
                'netincome': 40
            },
            2018: {
                'netcashfromcontinuingoperatingactivities': 50,
                'purchaseofplantpropertyandequipment': 50,
                'netincome': 50
            }
        }

        historical_revenue = {
            2014: 100,
            2015: 200,
            2016: 300,
            2017: 400,
            2018: 500
        }

        with patch.object(intrinio_data, 'get_historical_cashflow_stmt',
                          return_value=cashflow_statement):
            with patch.object(intrinio_data, 'get_historical_revenue',
                              return_value=historical_revenue):
                with patch.object(intrinio_data, 'get_outstanding_diluted_shares',
                                  return_value=1000):

                    dcf_model = JimmyDCFModel('aapl', 2018)
                    price = dcf_model.calculate_dcf_price()
                    self.assertEqual(price, 5.559189179051494)
