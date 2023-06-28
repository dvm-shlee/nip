import types
from .dataset import *
from .project import *

# parse module contents
_functions = []
_classes = []
_modules = []

for k, v in dict(globals()).items():
    if isinstance(v, types.FunctionType):
        _functions.append(k)
    if isinstance(v, type):
        _classes.append((k, v.__module__.split('.')[-1]))
    # filter the modules not want to expose
    if isinstance(v, types.ModuleType) and k not in ['os', 'types']:
        _modules.append(k)
    del k, v

# filter classes
_classes = [c for c, m in _classes if m in _modules]

__all__ = _functions + _classes + _modules