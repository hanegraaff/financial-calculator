import unittest
import logging
from test.test_dataprovider_intrinio_util import TestDataProviderIntrinioUtil
from test.test_exceptions import TestExceptions
from test.test_dataprovider_intrinio_data import TestDataProviderIntrinioData
from test.test_financial_calcularor import TestFinancialCalculator
from test.test_valuation_models_jimmy_model import TestJimmyModel
from test.test_support_financial_cache import TestFinancialCache
from test.test_reporting_workbook_report import TestWorkbookReport
from test.test_reporting_jimmy_report_worksheet import TestJimmyReportWorksheet

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] - %(message)s')


if __name__ == '__main__':
    unittest.main()