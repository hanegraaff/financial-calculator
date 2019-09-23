class BaseError(Exception):
    """ 
        Chained Exception used a basis for all errors.
        The cause should be a String or an Exception object 
        
        Attributes: 
            message: a string containing the error message
            cause: The cause of the exception. Must be an object that can be
                converted to a string
    """

    def __init__(self, message, cause):
        self.message = message
        self.cause = cause

    def __str__(self):
        return self.__print_cause__()

    def __repr__(self):
        return self.__print_cause__()

    def __print_cause__(self):
        if self.cause == None:
            return self.message

        return "%s. Caused by: %s" % (self.message, str(self.cause))

class ValidationError(BaseError):
    """
        A class representing a Validation Error
    """
    def __print_cause__(self):
        return "Validation Error: " + super().__print_cause__()

class DataError(BaseError):
    """
        A class representing a Financial Data error
    """
    def __print_cause__(self):
        return "Data Error: " + super().__print_cause__()

    

    