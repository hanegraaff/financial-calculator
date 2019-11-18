class Nop(object):
    def nop(self, *args, **kw): 
        pass

    def __getattr__(self, _): 
        return self.nop