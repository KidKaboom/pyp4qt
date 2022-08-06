# Project Modules
from pyp4qt.session import Session

# Python Modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QComboBox

class WorkspaceCombobox(QComboBox):
    def __init__(self, parent=None, session=None):
        QComboBox.__init__(self, parent)

        self._session = session

        if self._session and self._session.connected():
            for workspace in self._session.workspaces():
                self.addItem(workspace)

        if not self.count() > 1:
            self.setEnabled(False)




if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    with Session() as session:
        app = QtWidgets.QApplication()
        widget = WorkspaceCombobox(None, session)
        widget.show()

        sys.exit(app.exec_())
