"""Author: Mark Hanegraaff -- 2019
"""
import os
import os.path
from abc import ABC, abstractmethod
from exception.exceptions import ValidationError, ReportError
from support import util

from openpyxl import load_workbook

# can be overridden for testing purposed


class ReportWorksheet(ABC):
    """ 
        Abstract class representing a worksheet inside a spreadsheet report

        Attributes: 
            template_name (str): Name of the xlsx file template.
            template_path (str): Path of the xlsx file template. 
    """

    template_path = "./templates/"

    def __init__(self, template_name: str):
        super().__init__()

        # assign this to a local variable so that it can be mocked
        if template_name == None or len(template_name) == 0:
            raise ValidationError("Invalid parameters",  None)

        self.template_name = template_name

    @abstractmethod
    def prepare_worksheet(self, worksheet: object, report_parameters: dict):
        """
            preares the worksheet by writing the results of the calculations into
            the worksheet object loaded from the report template

            Parameters
            ----------
            worksheet : object
                openpyxl worksheet object loaded from the supplied template
            report_parameters : dict
                A dictionary of parameters used for this report.
                This dictionary is created by the dcf model and includes intermediate
                and final results.

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
        pass

    def create_worksheet(self, report_parameters: dict):
        """
            creates a worksheet object by loading the template and writing
            results into it.
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
        self.prepare_worksheet(wb.active, report_parameters)

        return wb.active

