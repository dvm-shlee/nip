import warnings

def warn(*args, **kwargs):
    warnings.warn(*args, **kwargs)

class InvalidFormatError(Exception):
    pass

