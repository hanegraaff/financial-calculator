import unittest
import logging
from test.test_dataprovider_intrinio_util import TestDataProviderIntrinioUtil
from test.test_exceptions import TestExceptions
from test.test_dataprovider_intrinio_data import TestDataProviderIntrinioData
from test.test_financial_calcularor import TestFinancialCalculator
from test.test_dcf_models_jimmy_model import TestJimmyModel
from test.test_reporting_jimmy_dcf_report import TestJimmyDCFReport
from test.test_support_financial_cache import TestFinancialCache

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] - %(message)s')


if __name__ == '__main__':
    unittest.main()