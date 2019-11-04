import unittest
from data_provider import intrinio_util
from exception.exceptions import ValidationError

class TestDataProviderIntrinioUtil(unittest.TestCase):
    
    '''
        get_fiscal_period tests
    '''
    def test_valid_date(self):
        (date_from, date_to) = intrinio_util.get_fiscal_year_period(2018, 0)

        self.assertEqual(date_from, "2018-01-01")
        self.assertEqual(date_to, "2018-12-31")

    def test_valid_date_extended(self):
        (date_from, date_to) = intrinio_util.get_fiscal_year_period(2018, 10)

        self.assertEqual(date_from, "2018-01-01")
        self.assertEqual(date_to, "2019-01-10")

    def test_invaid_date(self):
        with self.assertRaises(ValidationError):
            intrinio_util.get_fiscal_year_period(0, 0)

    def test_invaid_extendedby(self):
        with self.assertRaises(ValidationError):
            intrinio_util.get_fiscal_year_period(2018, -1)

        with self.assertRaises(ValidationError):
            intrinio_util.get_fiscal_year_period(2018, 360)
