import os
import imp
from fnmatch import fnmatch

modules = dict()
dirname = os.path.dirname(__file__)

for f in os.listdir('%s/modules/' % dirname):
    if fnmatch(f, '*.py'):
        module_name = f[:-3]
        mod = imp.load_source(module_name, '%s/modules/%s' % (dirname, f))
        modules[module_name] = mod

def get_modules():
    return modules