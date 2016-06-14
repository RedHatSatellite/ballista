# Copyright (c) 2016 the Ballista Project https://gitlab.com/parapet/ballista
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import os
import imp
from fnmatch import fnmatch

available_modules = dict()
dirname = os.path.dirname(__file__)

for f in os.listdir('%s/modules/' % dirname):
    if fnmatch(f, '*.py'):
        module_name = f[:-3]
        if module_name == '__init__':
            continue
        mod = imp.load_source(module_name, '%s/modules/%s' % (dirname, f))
        available_modules[module_name] = mod
