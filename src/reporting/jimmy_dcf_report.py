"""Author: Mark Hanegraaff -- 2019
"""
from exception.exceptions import ValidationError, ReportError
from reporting.spreadsheet_report import SpreadsheetReport


class JimmyDCFReport(SpreadsheetReport):
    """ 
        
        Jimmy DCF Report. Creates a spreadhseet with the Jimmy DCF
        Calculation results.

        Attributes: 
            None
    """

    def __init__(self, templateName: str):
        super().__init__(templateName)

    def prepare_report(self, worksheet : object, report_parameters : dict):

        try:
            # replace parameters
            worksheet.cell(row=7, column=2, value=report_parameters['long_term_growth_rate'])
            worksheet.cell(row=8, column=2, value=report_parameters['discount_rate'])
            worksheet.cell(row=11, column=7, value=report_parameters['outstanding_shares'])

            # replace multiplier
            worksheet.cell(row=15, column=7, value=report_parameters['calculated_growth_rate'])
            worksheet.cell(row=16, column=7, value=report_parameters['calculated_profit_margin'])
            worksheet.cell(row=17, column=7, value=report_parameters['calculated_fcfe_ni_ratio'])

            # update heading labels
            i = 0
            for year in range(report_parameters['history_start_year'], report_parameters['history_end_year'] + 1):
                worksheet.cell(row=1, column=2+i, value="FY %d" % year)
                worksheet.cell(row=14, column=2+i, value="FY %d" % year)
                i+=1

            i = 0
            for year in range(report_parameters['forecast_start_year'], report_parameters['forecast_end_year'] + 1):
                worksheet.cell(row=1, column=7+i, value="%d Forecast" % year)
                worksheet.cell(row=6, column=7+i, value="%d Forecast" % year)
                i+=1
            
            # replace financials
            i = 0
            for year in range(report_parameters['history_start_year'], report_parameters['history_end_year'] + 1):
                
                revenue = report_parameters['historical_revenue'][year]
                ni = report_parameters['historical_net_income'][year]
                fcfe = report_parameters['historical_fcfe'][year]

                worksheet.cell(row=2, column=2+i, value=revenue)
                worksheet.cell(row=3, column=2+i, value=ni)
                worksheet.cell(row=4, column=2+i, value=fcfe)
                i += 1

            return worksheet.cell(row=12, column=7).value
        except KeyError as ke:
            raise ReportError("Could not prepare report because of an error with report parameters", ke)


        
