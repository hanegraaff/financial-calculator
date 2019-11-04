"""Author: Mark Hanegraaff -- 2019
"""
import os
import os.path
from abc import ABC, abstractmethod
from exception.exceptions import ValidationError, ReportError


from openpyxl import load_workbook

# can be overridden for testing purposed

def init_report_dir():
    """
        Creates the report directory if not already present

        Parameters
        ------------
        None
        
        Returns
        ------------
        None
    """
    try:
        if not os.path.exists(SpreadsheetReport.output_path):
            os.makedirs(SpreadsheetReport.output_path)
    except Exception as e:
        raise ReportError("Can't create reports directory: %s" % SpreadsheetReport.output_path, e)


class SpreadsheetReport(ABC):
    """ 
        Abstract class representing the base for all spreadsheet based reports 

        Attributes: 
            template_name (str): Name of the xlsx file template.
            template_path (str): Path of the xlsx file template. 
            output_path (str): Path of the output report
    """

    template_path = "./templates/"
    output_path = "./reports/"

    def __init__(self, template_name: str):
        super().__init__()

        # assign this to a local variable so that it can be mocked
        if template_name == None or len(template_name) == 0:
            raise ValidationError("Invalid parameters",  None)

        self.template_name = template_name

    def generate_report(self, report_filename: str, report_parameters: dict):
        """
            Generates a report by updating a copy of the report template 
            and saving it to a new file. The report is prepared by implementing classes
            that override the 'prepare_report' method.
            The report is written to the 'output_path' folder using 'report_filename'
            as the output name.

            Parameters
            ----------
            report_filename : str
                Name of the output report
            report_parameters : dict
                A dictionary of parameters used for this report.
                Typically the same dictionary used to store intermediate results.

            Raises
            ----------
            ValidationError
                In case bad parameters are supplied
            ReportError
                In case of any errors preparing or generating the report.

            Returns
            -------
            None

        """
        if report_parameters == None:
            raise ValidationError(
                "Could not Generate Report. Invalid parameters",  None)

        try:
            wb = load_workbook(filename='%s%s' %
                               (self.template_path, self.template_name))
        except Exception as e:
            raise ReportError(
                "Could not Generate Report. Error reading template", e)

        # user implemented callback
        self.prepare_report(wb.active, report_parameters)

        output_report_name = '%s%s' % (self.output_path, report_filename)

        try:
            wb.save(output_report_name)
        except Exception as e:
            raise ReportError("Error saving report", e)

    @abstractmethod
    def prepare_report(self, worksheet: object, report_parameters: dict):
        pass

    # useful for testing
    def override_template_path(self, template_path: str):
        """
            Override template path. Used for testing
        """
        self.template_path = template_path

    def override_output_path(self, output_path: str):
        """
            Override output path. Used for testing
        """
        self.output_path = output_path
