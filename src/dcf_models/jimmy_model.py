"""Author: Mark Hanegraaff -- 2019
"""

from dcf_models.base_model import BaseDCFModel

from data_provider import intrinio_data
from financial import calculator
import math
import datetime
import statistics
from datetime import timedelta
from exception.exceptions import ValidationError, CalculationError, DataError, ReportError
import logging
from support import util
from reporting.jimmy_dcf_report import JimmyDCFReport

log = logging.getLogger()

class JimmyDCFModel(BaseDCFModel):

    """
        Computes a DCF calculation based on a variation of the "Jimmy" method, which
        is based this video:

        https://www.youtube.com/watch?v=fd_emLLzJnk&t=500s

        These are the steps
        -------------------
        1) Generate 4 years of historical free cash flow to equity (y-4, y)
        2) Generate 4 years of historical net income
        3) Determine the FCFE / net income for both sets and pick the most
           conservative number. Alternatively it could be an average of all
           numbers.
        4) Generate 4 years of historical revenue. Determine average growth, and
           and Forecast the next 4 years. The video suggests using two years of
           analyst forecast. Here we use the historical average.
        5) Determine historical profit margin (net margin) by dividing net income
           by revenue. Ideally the profit margin shoul be fairly consistent.
        6) Forecast net income by multipling revenue by profit margin
        7) Forecast FCFE by multiplying net income by the number determined in step 3.
        8) Determine cost of capital. Currently hardcoded.
        9) Apply the DCF forumla using free cash flow forecasts, growth estimate and
           discount rates.
        10) Deternine shares outstanding
        11) Determine value per share by diving DCF value with shares outstanding

        This model will produce a reasonable number for companies with the
        following characteristics:

        1) Company pays little or no dividends
        2) Free cash flow aligns with profitability
        3) Inverstor is able to take a control perspective
    """

    def __init__(self, ticker : str, fiscal_year : int):
        super().__init__(ticker, fiscal_year)

        self.report_template = "dcf_jimmy_template.xlsx"

    def calculate_dcf_price(self):
        """
            Computes the DCF Price using a variation of the Jimmy method

            Parameters
            ----------
            None

            Raises
            ----------
            DataError 
                In case or any errors reading financial data
            CalculationError
                In case the supplied financial data is not suitable
                to perform the necessary calculations

            Returns
            -------
                A float with calculated DCF price value
        """
        #
        # Gather all necessary data
        #
        cashflow_statements = intrinio_data.get_historical_cashflow_stmt(
            self.ticker, self.history_start_year, self.history_end_year, None)

        # get historical fcfe
        historical_fcfe = calculator.get_historical_simple_fcfe(cashflow_statements)
        self.intermediate_results['historical_fcfe'] = historical_fcfe

        # get historical net income
        historical_net_income = calculator.get_historical_net_income(cashflow_statements)
        self.intermediate_results['historical_net_income'] = historical_net_income

        # get historical revenue growth and determine growth rate
        historical_revenue = intrinio_data.get_historical_revenue(
            self.ticker, self.history_start_year, self.history_end_year)
        self.intermediate_results['historical_revenue'] = historical_revenue
        
        # Get Shares outstanding
        outstanding_shares = intrinio_data.get_outstanding_diluted_shares(self.ticker, self.fiscal_year)
        self.intermediate_results['outstanding_shares'] = outstanding_shares

        #
        # Calculate fcfe_ni_ratio, revenue growth and profit margin
        # These will be used to estimate the cash flow
        #

        # get fcfe_ni_ratio
        fcfe_ni_ratio = self.__calc_fcfe_ni_ratio__(historical_fcfe, historical_net_income)
        revenue_growth = self.__calc_revenue_growth_rate__(historical_revenue)

        # calculate histotical profit margin
        profit_margin = self.__calc_profit_margin__(historical_net_income, historical_revenue)
        revenue_forecast = self.__forecast_revenue__(historical_revenue[self.history_end_year], revenue_growth)
        net_income_forecast = self.__forecast_net_income__(revenue_forecast, profit_margin)
        fcfe_forecast = self.__forecast_fcfe__(net_income_forecast, fcfe_ni_ratio)

        # Perform DCF Calculation and figure out enterprise value
        (enteprise_value, intermediate_results) = calculator.calc_enterprise_value(fcfe_forecast, self.long_term_growth_rate, self.discount_rate)
        
        self.intermediate_results.update(intermediate_results)

        self.intermediate_results['sum_discounted_cash_flows'] = sum(self.intermediate_results['discounted_cashflows'].values())
        intrinsic_value_per_share = enteprise_value / outstanding_shares

        self.intermediate_results['intrinsic_value_per_share'] = intrinsic_value_per_share
        return intrinsic_value_per_share

    
    def generate_report(self):
        report = JimmyDCFReport(self.report_template)
        try:
            report.generate_report('%s-%d.xlsx' % (self.intermediate_results['ticker'], self.intermediate_results['history_end_year']), self.get_itermediate_results())
        except KeyError as ke:
            raise ReportError("Could not generate report because output name was invalid", ke)
    
    def __calc_fcfe_ni_ratio__(self, hist_fcfe : dict, hist_net_income : dict):
        """
            calculates the fcfe to net income ratio using this formula

            fcfe_ni_ratio[year] = (hist_fcfe[year] / hist_net_income[year]) - 1

            then returns the median value as a factor, e.g.
            0.03

            Parameters
            ----------
            hist_fcfe : dict
                A dictionary of historical free cash flow to equity
            hist_net_income : dict
                A dictionary of historical net incomes

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
                A float with the calculated fcfe/ni ratio
        """

        fcfe_ni_ratio = {}

        try:
            for i in range(self.history_start_year, self.history_end_year + 1):
                fcfe_ni_ratio[i] = hist_fcfe[i] / hist_net_income[i]
        except KeyError as ke:
            raise CalculationError("Could not calculate fcfe_ni_ratio because there wan not enough history", ke)

        calculated_fcfe_ni_ratio = statistics.median(list(fcfe_ni_ratio.values()))

        self.intermediate_results['fcfe_ni_ratio'] = fcfe_ni_ratio
        self.intermediate_results['calculated_fcfe_ni_ratio'] = calculated_fcfe_ni_ratio

        return calculated_fcfe_ni_ratio

    def __calc_profit_margin__(self, hist_net_income : dict, hist_revenue : dict):
        """
            Calculates the historical profit margin using this formula:

            net_income(year) / revenue(year)

            Then return the median value as a factor, e.g.
            0.23

            Parameters
            ----------
            hist_net_income : dict
                A dictionary of historical net incomes
            hist_revenue : dict
                A dictionary of historical revenues

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
                A float with the calculated profit margin as a factor

        """

        hist_profit_margin = {}

        try:
            for i in range(self.history_start_year, self.history_end_year + 1):
                hist_profit_margin[i] = hist_net_income[i] / hist_revenue[i]
        except KeyError as ke:
            raise CalculationError("Could not calculate profit margin because there wan not enough history", ke)

        calculated_profit_margin = statistics.median(list(hist_profit_margin.values()))

        self.intermediate_results['hist_profit_margin'] = hist_profit_margin
        self.intermediate_results['calculated_profit_margin'] = calculated_profit_margin

        return calculated_profit_margin
        
    def __calc_revenue_growth_rate__(self, hist_revenue :  dict):
        '''
            Calculates the historical revenue growth rate using this formula

            revenue(year + 1) / revenue(year)

            Then return the median value

            Parameters
            ----------
            hist_revenue : dict
                A dictionary of historical revenues

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
                A float with the calculated growth rate as a factor
        '''

        hist_revenue_growth = {}

        try:
            for year in range(self.history_start_year, self.history_end_year):
                hist_revenue_growth[year + 1] = (hist_revenue[year + 1]/hist_revenue[year]) - 1
        except KeyError as ke:
            raise CalculationError("Could not calculate revenue growth because there wan not enough history", ke)

        calculated_growth_rate = statistics.median(list(hist_revenue_growth.values()))

        self.intermediate_results['hist_revenue_growth'] = hist_revenue_growth
        self.intermediate_results['calculated_growth_rate'] = calculated_growth_rate

        return calculated_growth_rate

    def __forecast_revenue__(self, latest_revenue : int, growth_rate : float):
        '''
            Forecasts the revenue given the latest value and a growth rate.
            Returns a dictionary with forecast values for the forecasting range
            For example:
            {
                2020: 100000000
                2021: 110000000
                2022: 120000000
                ...
            }

            Parameters
            ----------
            latest_revenue : int
                The most current revenue value
            growth_rate : float
                The revenue growth rate

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
                A float with the calculated growth rate as a factor
        '''

        revenue_forecast = {}

        next_forecast = latest_revenue * (1 + growth_rate)

        try:
            for forecast_year in range(self.forecast_start_year, self.forecast_end_year + 1):
                revenue_forecast[forecast_year] = next_forecast
                next_forecast = next_forecast * (1 + growth_rate)
        except KeyError as ke:
            raise CalculationError("Could not forecast revenue because because not enough data was supplied", ke)

        self.intermediate_results['revenue_forecast'] = revenue_forecast

        return revenue_forecast

    def __forecast_net_income__(self, revenue_forecast : dict, profit_margin : float):
        '''
            Returns a dictionary of net income forecasts based on the supplied revenues 
            forecasts and profit margin

            net_income_forecast[year] = revenue_forecast[year] * profit_margin

            Parameters
            ----------
            revenue_forecast : dict
                A dictionary containing the revenue forecast
            profit_margin : float
                The calculated profit margin

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
                A dictionary containing the net income forecast
        '''
        net_income_forecast = {}
        
        try:
            for year in range(self.forecast_start_year, self.forecast_end_year + 1):
                net_income_forecast[year] = revenue_forecast[year] * profit_margin
        except KeyError as ke:
            raise CalculationError("Could not forecast net income because because not enough data was supplied", ke)

        self.intermediate_results['net_income_forecast'] = net_income_forecast

        return net_income_forecast

    def __forecast_fcfe__(self, net_income_forecast :  dict, fcfe_ni_ratio : float):
        '''
            Returns a dictionary of fcfe forecasts based on the supplied net margin forecasts
            and multiplier

            fcfe_forecast[year] = net_income_forecast[year] * fcfe_ni_ratio

            Parameters
            ----------
            net_income_forecast : dict
                A dictionary containing the net income forecast
            fcfe_ni_ratio : float
                The calculated fcfe/ni ratio

            Raises
            ----------
            CalculationError
                In case of insufficient or missing data in
                the supplied dictionaries

            Returns
            -------
            A dictionary containing the fcfe forecast

        '''
        fcfe_forecast = {}
        try:
            for year in range(self.forecast_start_year, self.forecast_end_year + 1):
                fcfe_forecast[year] = net_income_forecast[year] * fcfe_ni_ratio
        except KeyError as ke:
            raise CalculationError("Could not forecast free cash flow because not enough data was supplied", ke)

        self.intermediate_results['fcfe_forecast'] = fcfe_forecast

        return fcfe_forecast
