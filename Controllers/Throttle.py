import time
from functools import partial


class ThrottleDecorator(object):
    def __init__(self, func, interval) -> None:
        self.func = func
        self.interval = interval
        self.last_called = 0
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)
    
    def __call__(self, *args, **kwds):
        now = time.time()
        if now - self.last_called > self.interval:
            self.last_called = now
            return self.func(*args, **kwds)
        else:
            return None
