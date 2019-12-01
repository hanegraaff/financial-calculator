import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from exception.exceptions import ReportError, ValidationError
from reporting.jimmy_report_worksheet import JimmyReportWorksheet
import os.path
import os


class TestJimmyReportWorksheet(unittest.TestCase):

    def test_report_invalid_parameters(self):
        report_params = {}

        report = JimmyReportWorksheet()

        with self.assertRaises(ReportError):
            report.create_worksheet(report_params)


    def test_report_no_parameters(self):
        report = JimmyReportWorksheet()

        with self.assertRaises(ValidationError):
            report.create_worksheet(None)


    def test_report_invalid_template(self):
        report_params = {}

        report = JimmyReportWorksheet()
        report.template_name = 'non-existent-template'

        with self.assertRaises(ReportError):
            report.create_worksheet(report_params)
            

    



        

    

