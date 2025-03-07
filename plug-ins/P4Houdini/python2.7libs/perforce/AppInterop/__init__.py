import imp
import os
import sys
import re
import logging
import glob

import pyp4qt.utils as Utils

def loadInteropModule(name, path):
    file, filename, data = imp.find_module( name, [cwd])
    mod = imp.load_module(name, file, filename, data)

    return name, mod


cwd = os.path.dirname(os.path.realpath(__file__))

modules = glob.glob(os.path.join(cwd,'*'))

# Only allow __init__.py based modules (in folders) to make things simpler
modules = filter(lambda x: not x.endswith('.py'), modules)
modules = filter(lambda x: not x.endswith('.pyc'), modules)

# Get only the relative directory paths
modules = [os.path.basename(x) for x in modules]

for module in modules:
    name, mod = loadInteropModule(module, cwd)

    try:
        if not mod.validate():
            continue
    except AttributeError as e:
        Utils.logger().debug('%s has no validate() method, skipping' % name)
        continue

    Utils.logger().info("Configuring for %s" % name)
    mod.setup()
    submodule = getattr(mod, 'interop')
    interop = getattr(submodule, name)
    break
else:
    interop = None


# interop = __import__('perforce.interop.maya', fromlist=['maya'])
# print getattr(interop, 'maya')


# # Import app specific utilities, maya opens scenes differently than nuke etc
# # Are we in maya or nuke?
# if re.match("maya", os.path.basename(sys.executable), re.I):
#     Utils.logger().info("Configuring for Maya")
#     interop = Utils.import_class('perforce.interop.maya', 'maya')

# elif re.match("nuke", os.path.basename(sys.executable), re.I):
#     Utils.logger().info("Configuring for Nuke")
#     interop = Utils.import_class('perforce.interop.nuke', 'nuke')

# elif in_unittest:
#     Utils.logger().info("Configuring for testing")
#     interop = Utils.import_class('perforce.interop.standalone', 'standalone')

# else:
#     Utils.logger().warning("Couldn't find app configuration")
#     raise ImportError(
#         "No supported applications found that this plugin can interface with")

