"""Author: Mark Hanegraaff -- 2019
"""
from io import BytesIO
from diskcache import Cache
from support import util
from exception.exceptions import ValidationError
import logging

log = logging.getLogger()

class FinancialCache():
    """
        A Disk based database containing an offline version of financial
        data and used as a cache 
    """
    
    def __init__(self, path, **kwargs):
        '''
            Initializes the cache

            Parameters
            ----------
            path : str
            The path where the cache will be located

            max_cache_size_bytes : int (kwargs)
            the maximum size of the cache in bytes

            
            Returns
            -----------
            A tuple of strings containing the start and end date of the fiscal period
        '''

        try:
            max_cache_size_bytes = kwargs['max_cache_size_bytes']
        except KeyError:
            # default max cache is 4GB
            max_cache_size_bytes = 4e9

        util.create_dir(path)
        
        try:
            self.cache = Cache(path, size_limit=int(max_cache_size_bytes))
        except Exception as e:
            raise ValidationError('invalid max cache size', e)

        log.debug("Cache was initialized: %s" % path)

    def write(self, key : str, value : object):
        self.cache[key] = value

    def read(self, key):
        try:
            return self.cache[key]
        except KeyError:
            log.debug("%s not found inside cache" % key)
            return None

    def close(self):
        self.cache.close()


cache = FinancialCache("./financial-data/")