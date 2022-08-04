from PySide2 import QtCore, QtGui, QtWidgets
from pyp4qt.apps import interop
from pyp4qt import perforce_utils

def displayErrorUI(e):
    error_ui = QtWidgets.QMessageBox()
    # error_ui.setWindowFlags(QtCore.Qt.WA_DeleteOnClose)

    eMsg, type = perforce_utils.parsePerforceError(e)

    if type == "warning":
        error_ui.warning(interop.main_parent_window(), "Perforce Warning", eMsg)
    elif type == "error":
        error_ui.critical(interop.main_parent_window(), "Perforce Error", eMsg)
    else:
        error_ui.information(interop.main_parent_window(), "Perforce Error", eMsg)

    error_ui.deleteLater()