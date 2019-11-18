import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from exception.exceptions import ReportError, ValidationError
from reporting.jimmy_dcf_report import JimmyDCFReport
import os.path
import os

template_path_override = "./test/spreadsheet/"
report_output_override = "./test/spreadsheet/"
test_template_name = "test_template.xlsx"
test_out_name = "out.xlsx"

class TestJimmyDCFReport(unittest.TestCase):

    def test_report_no_template(self):
        report_params = {}


        report = JimmyDCFReport("non-existent-template.xlsx")

        with self.assertRaises(ReportError):
            report.generate_report('out.xlsx', report_params)

    
    def test_no_template(self):
        with self.assertRaises(ValidationError):
            JimmyDCFReport(None)
    

    def test_report_invalid_parameters(self):
        report_params = {}

        report = JimmyDCFReport(test_template_name)

        report.override_template_path(template_path_override)
        report.override_output_path(report_output_override)
        
        with self.assertRaises(ReportError):
            report.generate_report(test_out_name, report_params)

    def test_report_no_parameters(self):
        report = JimmyDCFReport(test_template_name)

        with self.assertRaises(ValidationError):
            report.generate_report(test_out_name, None)

    def test_save_invalid_report_out_path(self):

        report = JimmyDCFReport(test_template_name)
        report.override_template_path(template_path_override)
        report.override_output_path(report_output_override + "non-existent-path/report-out")

        with patch.object(report, 'prepare_report', return_value=None):
            with self.assertRaises(ReportError):
                report.generate_report(test_out_name, {})

    def test_save_valid_report(self):
    
        report = JimmyDCFReport(test_template_name)

        report.override_template_path(template_path_override)
        report.override_output_path(report_output_override)

        with patch.object(report, 'prepare_report', return_value=None):
            report.generate_report(test_out_name, {})

        file_exists = os.path.isfile(report_output_override + test_out_name)

        if file_exists == True:
            os.remove(report_output_override + test_out_name)

        self.assertTrue(file_exists)

            

    



        

    

