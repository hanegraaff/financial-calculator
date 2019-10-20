"""Author: Mark Hanegraaff -- 2019
"""

from abc import ABC, abstractmethod
 
class BaseDCFModel(ABC):
    """
        Base class for all DCF Models.
        The current implementation supports the following features:
        1) A consistent method to compute the DCF price
        2) A dictionary of intermediate results that can be used
           for debugging purpose
    """

    intermediate_results = {}
 
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def calculate_dcf_price(self, ticker : str, year : str):
        pass

    def get_itermediate_results(self):
        return self.intermediate_results

    def reset_intermediate_results(self):
        self.intermediate_results = {}
