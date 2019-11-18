import unittest
import shutil
from support.financial_cache import FinancialCache
from exception.exceptions import ValidationError, FileSystemError


class TestFinancialCache(unittest.TestCase):

    test_path = "./test/cache-unittest/"
    test_cache = None

    @classmethod
    def setUpClass(cls):
        cls.test_cache = FinancialCache(cls.test_path)
        
    @classmethod
    def tearDownClass(cls):
        cls.test_cache.close()
        shutil.rmtree(cls.test_path)

    def test_no_cache_path(self):
        with self.assertRaises(FileSystemError):
            FinancialCache(None)

    def test_int_value(self):
        key = 'test-int'
        value = 1234

        self.test_cache.write(key, value)
        self.assertTrue(self.test_cache.read(key), value)


    def test_string_value(self):
        key = 'test-string'
        value = "1234"

        self.test_cache.write(key, value)
        self.assertEqual(self.test_cache.read(key), value)

    def test_dict_value(self):
        key = 'test-dict'
        value = {"a":1, "b":2}

        self.test_cache.write(key, value)
        self.assertEqual(self.test_cache.read(key)["a"], 1)
        self.assertEqual(self.test_cache.read(key)["b"], 2)

    
    def test_value_not_found(self):
        key = 'not-found'
        self.assertEqual(self.test_cache.read(key), None)

    def test_bad_cache_size(self):
        bad_cache_path = "./test/cache-unittest-bad/"
        with self.assertRaises(ValidationError):
            FinancialCache(bad_cache_path, max_cache_size_bytes="BAD_VAUE")

    def test_cache_out_of_space(self):

        small_cache_path = "./test/cache-unittest-small/"
        test_string = "x"
        for i in range(0, 10 * 1000): test_string += "x"

        small_test_cache = FinancialCache(small_cache_path, max_cache_size_bytes=100)

        try:
            small_test_cache.write("test-key", test_string)
            self.assertEqual(small_test_cache.read("test-key"), None)

        finally:
            shutil.rmtree(small_cache_path)
        
        

