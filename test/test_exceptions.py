import unittest
from exception.exceptions import ValidationError

class TestExceptions(unittest.TestCase):
    
    '''
        ValidationError
    '''
    def test_simple_exception_nocause(self):

        ve = ValidationError("Cannot do XYZ", None)
        self.assertEqual(str(ve), "Validation Error: Cannot do XYZ")

    def test_simple_exception_with_exceptioncause(self):

        empty_dict = {}

        try:
            empty_dict['XXX']
            self.fail("Error in test setup")
        except KeyError as ke:
            ve = ValidationError("Cannot do XYZ", ke)
            self.assertEqual(str(ve), "Validation Error: Cannot do XYZ. Caused by: 'XXX'")

    def test_simple_exception_with_stringcause(self):
    
        ve = ValidationError("Cannot do XYZ", "Some Error")

        self.assertEqual(str(ve), "Validation Error: Cannot do XYZ. Caused by: Some Error")

    def test_simple_exception_with_numbercause(self):
        
        ve = ValidationError("Cannot do XYZ", 3.2)

        self.assertEqual(str(ve), "Validation Error: Cannot do XYZ. Caused by: 3.2")

    def test_simple_exception_with_chainedcause(self):

        root_cause = Exception("Root Cause")
        chained_cause = Exception("Some reason", root_cause)

        ve = ValidationError("Cannot do XYZ", chained_cause)

        self.assertEqual(str(ve), "Validation Error: Cannot do XYZ. Caused by: ('Some reason', Exception('Root Cause'))")