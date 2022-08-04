# Project Modules
from pyp4qt.session import Session, DepotFile, DepotDirectory, P4Exception

# Python Modules
import os
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt


class ChangeListItem(object):
    def __init__(self, parent=None):
        self._parent = parent


class ChangeListModel(QAbstractItemModel):
    def __init__(self, parent=None, session=None):
        QAbstractItemModel.__init__(self, parent)

        self._session = session
        self._root = ChangeListItem()

    def isValid(self):
        """ Returns if the current session is valid and is connected.

        Returns:
            bool
        """
        return self._session and self._session.connected()


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    app = QtWidgets.QApplication()
    session = Session()
    session.connect()

    view = QtWidgets.QTreeView()
    model = ChangeListModel(view, session)
    view.setModel(model)
    view.show()

    session.disconnect()
    sys.exit(app.exec_())
