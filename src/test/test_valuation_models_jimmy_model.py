import unittest
from exception.exceptions import ValidationError, CalculationError, ReportError
from valuation_models.jimmy_model import JimmyValuationModel
from data_provider import intrinio_data
from unittest.mock import patch
from support import util

 
class TestJimmyModel(unittest.TestCase):

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

    def test_dcf_no_symbol(self):
        with self.assertRaises(ValidationError):
            dcf_model = JimmyValuationModel(None, 2018)
            dcf_model.calculate_dcf_price()

    
    def test_dcf_with_valid_parameters(self):
        """
            Tests that the results of a DCF calculation are correct
            after tweaking some of its parameters, namely long term growth rate
            and discount rate

            Results are reconciled with the template spreadsheet
        """

        dcf_model = JimmyValuationModel('aapl', 2018)

        with patch.object(intrinio_data, 'get_historical_cashflow_stmt',
                          return_value=self.cashflow_statement), \
             patch.object(intrinio_data, 'get_historical_revenue',
                              return_value=self.historical_revenue), \
             patch.object(intrinio_data, 'get_outstanding_diluted_shares',
                                  return_value=1000):

                dcf_model.discount_rate = 0.0975
                dcf_model.long_term_growth_rate = 0.025

                price = dcf_model.calculate_dcf_price()

                self.assertEqual(round(price, 3), 4.618)
            
                dcf_model.discount_rate = .08
                price = dcf_model.calculate_dcf_price()

                self.assertEqual(round(price, 3), 6.208)

                dcf_model.discount_rate = 1
                price = dcf_model.calculate_dcf_price()
                self.assertEqual(round(price, 3), 0.208)


    def test_dcf_with_invalid_parameters(self):
        """
            Tests that the results of a DCF calculation are correct
            after tweaking some of its parameters, namely long term growth rate
            and discount rate
        """

        dcf_model = JimmyValuationModel('aapl', 2018)

        with patch.object(intrinio_data, 'get_historical_cashflow_stmt', 
                            return_value=self.cashflow_statement), \
             patch.object(intrinio_data, 'get_historical_revenue', 
                            return_value=self.historical_revenue), \
             patch.object(intrinio_data, 'get_outstanding_diluted_shares', 
                            return_value=1000):

                with self.assertRaises(CalculationError):
                    dcf_model.discount_rate = 0
                    dcf_model.long_term_growth_rate = 1
                    dcf_model.calculate_dcf_price()
                
                with self.assertRaises(CalculationError): 
                    dcf_model.discount_rate = 1
                    dcf_model.long_term_growth_rate = 0
                    dcf_model.calculate_dcf_price()

                with self.assertRaises(CalculationError):
                    dcf_model.discount_rate = 1
                    dcf_model.long_term_growth_rate = 1
                    dcf_model.calculate_dcf_price()

                with self.assertRaises(CalculationError):
                    dcf_model.discount_rate = 5
                    dcf_model.long_term_growth_rate = 10
                    dcf_model.calculate_dcf_price()
                

    '''def test_generate_invalid_report(self):

        dcf_model = JimmyValuationModel('aapl', 2018)

        # test that the report won't be generated if calculations are
        # missing
        with self.assertRaises(ReportError):
            dcf_model.generate_report()

        # test that report generation will not be attempted if no pamameters
        # are supplied
        dcf_model.intermediate_results = {}
        with self.assertRaises(ReportError):
            dcf_model.generate_report()'''







