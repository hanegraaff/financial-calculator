"""Author: Mark Hanegraaff -- 2019
"""

from abc import ABC, abstractmethod
from exception.exceptions import ValidationError
 
class BaseValudationModel(ABC):
    """
        Base class for all Valudation Models.
        The current implementation supports the following features:
        1) A consistent method to compute the DCF price
        2) A dictionary of intermediate results that can be used
           for debugging purpose
    """

    intermediate_results = {}

    HISTORY_YEARS = 4
    FORECAST_YEARS = 4
 
    def __init__(self, ticker : str, fiscal_year : str):
        super().__init__()

        self.ticker = ticker
        self.fiscal_year = fiscal_year

        if (ticker == None or len(ticker) == 0):
            raise ValidationError("Invalid Ticker Symbol", None)

        self.discount_rate = 0.0975
        self.long_term_growth_rate = 0.025

        self.history_start_year = fiscal_year - self.HISTORY_YEARS
        self.history_end_year = fiscal_year

        self.forecast_start_year = self.fiscal_year + 1
        self.forecast_end_year = self.fiscal_year + self.FORECAST_YEARS

        self.__reset_intermediate_results__()
    

    @abstractmethod
    def calculate_dcf_price(self):
        """
            Calculates the DCF Prie of a security.
            See implementing classes for details.
        """
        pass


    def get_itermediate_results(self):
        '''
            Returns the intermediate and final results of this model's
            calculation as a dictionary. The contents vary by calculation, 
            however some basic information like the ticker symbol and the
            range of history and forecast years stay the same.

            Parameters
            ----------
            None.

            Returns
            -------
            A dictionary containing the results of the calculation. These are
            used for testing and reporting
        '''
        return self.intermediate_results

    def __reset_intermediate_results__(self):

        '''
            Resets the dictionary of intermediate results.

            Parameters
            ----------
            None

            Returns
            -------
            None
        '''
        
        self.intermediate_results = {}
        
        # populate the intermediate results with basic information
        self.intermediate_results['discount_rate'] = self.discount_rate
        self.intermediate_results['long_term_growth_rate'] = self.long_term_growth_rate
        self.intermediate_results['ticker'] = self.ticker
        self.intermediate_results['history_start_year'] = self.history_start_year
        self.intermediate_results['history_end_year'] = self.history_end_year
        self.intermediate_results['forecast_start_year'] = self.forecast_start_year
        self.intermediate_results['forecast_end_year'] = self.forecast_end_year
        self.intermediate_results['discount_rate'] = self.discount_rate
        self.intermediate_results['long_term_growth_rate'] = self.long_term_growth_rate

