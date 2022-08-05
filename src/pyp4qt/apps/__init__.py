import importlib
import importlib.util
import os
import sys
import re
import logging
import glob

from pyp4qt import utils

cwd = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("Perforce")

def loadInteropModule(name, path):
    # file, filename, data = imp.find_module( name, [cwd])
    # mod = imp.load_module(name, file, filename, data)
    # return name, mod
    spec = importlib.util.find_spec(name, path)
    mod = importlib.util.module_from_spec(spec)

    if mod:
        spec.loader.exec_module(mod)

    return mod


modules = glob.glob(os.path.join(cwd, '*'))

# Only allow __init__.py based modules (in folders) to make things simpler
modules = filter(lambda x: not x.endswith('.py'), modules)
modules = filter(lambda x: not x.endswith('.pyc'), modules)

# Get only the relative directory paths
modules = [os.path.basename(x) for x in modules]
interop = None

for module in modules:
    module_name = "pyp4qt.apps.{}".format(module)
    mod = loadInteropModule(module_name, cwd)

    try:
        if not mod.validate():
            continue
    except AttributeError as e:
        logger.debug('%s has no validate() method, skipping' % module)
        continue

    logger.info("Configuring for %s" % module)
    mod.setup()
    # submodule = getattr(mod, 'interop')
    submodule = loadInteropModule("{}.adapter".format(module_name), os.path.join(cwd, module))
    interop = getattr(submodule, module)
    break