import os
import re
import traceback
import logging
import platform
from distutils.version import StrictVersion

from P4 import P4, P4Exception, Progress, OutputHandler

import pyp4qt.utils as Utils
import PerforceMenu
from pyp4qt.apps import interop

# try:
#     AppUtils.close_window(qt.perforceMenu)
# except:
#     qt = None

def initMenu(p4):
    global ui
    # try:
    #     # cmds.deleteUI(qt.perforceMenu)
    #     AppUtils.close_window(qt.perforceMenu)
    # except:
    #     pass

    # interop.initCallbacks()

    try:
        ui = PerforceMenu.MainShelf(p4)

        ui.addMenu()
    except ValueError as e:
        Utils.logger().critical(e)

    # mu.executeDeferred('qt.addMenu()')


def cleanupMenu():
    global ui

    # interop.cleanupCallbacks()

    # try:
    #     # cmds.deleteUI(qt.perforceMenu)
    #     AppUtils.close_window(qt.perforceMenu)
    # except Exception as e:
    #     raise e

    ui.close()

    #del qt