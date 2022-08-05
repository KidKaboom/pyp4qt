import os
import re
import traceback
import logging
import platform
from distutils.version import StrictVersion

from P4 import P4, P4Exception, Progress, OutputHandler

import pyp4qt.utils as Utils
import pyp4qt.qt.PerforceMenu as PerforceMenu
from pyp4qt.apps import interop

# try:
#     AppUtils.closeWindow(qt.perforceMenu)
# except:
#     qt = None

def initMenu(p4):
    global ui
    # try:
    #     # cmds.deleteUI(qt.perforceMenu)
    #     AppUtils.closeWindow(qt.perforceMenu)
    # except:
    #     pass

    # interop.initCallbacks()

    try:
        ui = PerforceMenu.MainShelf(p4)

        ui.addMenu()
    except ValueError as e:
        Utils.p4Logger().critical(e)

    # mu.executeDeferred('qt.addMenu()')


def cleanupMenu():
    global ui

    # interop.cleanupCallbacks()

    # try:
    #     # cmds.deleteUI(qt.perforceMenu)
    #     AppUtils.closeWindow(qt.perforceMenu)
    # except Exception as e:
    #     raise e

    ui.close()

    #del qt