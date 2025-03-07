import unittest
import logging
import os
import sys

from pyp4qt import utils
from test_perforce import TestingEnvironment, setupPythonEnvironment
setupPythonEnvironment()

from pyp4qt.utils import logger
from pyp4qt.apps import interop
from pyp4qt.qt import PerforceMenu


# This is a convenient way of automatically loading up a specific menu entry for testing
# Clicking on stuff in a menu is tedious
def displayMenuItem(ui, args):
    menuEntries = {
            "checkout.file":                    ui.checkoutFile,
            "checkout.folder":                  ui.checkoutFolder,
            "mark.delete":                      ui.deleteFile,
            "show.changelist":                  ui.queryOpened,
            "submit.change":                    utils.submit_change,
            "sync.all":                         ui.syncAllChanged,
            "sync.all.force":                   ui.syncAll,
            "depot.history":                    ui.fileRevisions,

            "file.status":                      ui.querySceneStatus,

            "create.asset":                     ui.createAsset,
            "create.shot":                      ui.createShot,
            "login.user":                       ui.loginAsUser,
            "server.info":                      ui.queryServerStatus,
            "create.workspace":                 ui.createWorkspace,
            "set.current.workspace":            ui.setCurrentWorkspace,
            "delete.pending":                   ui.deletePending
    }

    for arg in args:
        if arg in menuEntries:
            try:
                menuEntries[arg]()
            except Exception as e:
                raise
        else:
            logger().warning('%s isn\'t a key in the menu item dict' % arg)

def setup(args):
    cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
    os.environ["P4CONFIG"] = os.path.join(cwd, '.p4config')

    window, app = interop.setup_env()
    logging.basicConfig(level=logging.DEBUG)

    p4 = TestingEnvironment()

    logger().debug('Default cwd: %s' % p4.cwd)

    ui = PerforceMenu.MainShelf(p4)

    if args:
        displayMenuItem(ui, args)
    else:
        ui.addMenu()
        window.show()

    app.exec_()

if __name__ == '__main__':
    args = sys.argv[1:]
    setup(args)