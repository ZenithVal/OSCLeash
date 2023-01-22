from functools import wraps
import time

# Useful wrapper for debugging
def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print ('func:%r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return wrap