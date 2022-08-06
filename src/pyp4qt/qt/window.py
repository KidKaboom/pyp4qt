# Project Modules
from pyp4qt.session import Session
from pyp4qt.qt.depot_model import DepotModel
from pyp4qt.qt.pending_model import PendingModel

# Python Modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QTreeView, QTabWidget, QFileSystemModel


class Window(QMainWindow):
    def __init__(self, parent=None, session=None):
        QMainWindow.__init__(self, parent)
        self._session = session
        self._info = dict()

        # Layout
        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        layout.addWidget(splitter)

        # Depot / Workspace Tab
        depot_tab = QTabWidget()
        splitter.addWidget(depot_tab)

        # Depot Model / View
        self._depot_model = DepotModel(self, self._session)
        self._depot_view = QTreeView(self)
        self._depot_view.setHeaderHidden(True)
        self._depot_view.setModel(self._depot_model)
        depot_tab.addTab(self._depot_view, "Depot")

        # Workspace Model / View
        self._workspace_model = QFileSystemModel()
        self._workspace_view = QTreeView()
        self._workspace_view.setModel(self._workspace_model)
        depot_tab.addTab(self._workspace_view, "Workspace")

        # Changlist Tab
        changelist_tab = QTabWidget()
        splitter.addWidget(changelist_tab)

        # Pending Changlist
        self._pending_model = PendingModel(self, self._session)
        self._pending_view = QTreeView()
        self._pending_view.setModel(self._pending_model)
        changelist_tab.addTab(self._pending_view, "Pending")

        if self._session:
            self.setSession(session)

    def setSession(self, session):
        self._session = session

        if not self._session or not self._session.connected():
            return

        info = self._session.info()
        title = "Perforce DCC - {}".format(", ".join([
            info["clientName"],
            info["clientHost"],
            info["serverName"],
            info["userName"]
        ]))

        self.setWindowTitle(title)
        self._info = info

        # Update Workspace
        index = self._workspace_model.setRootPath(info["clientRoot"])
        self._workspace_view.setRootIndex(index)
        return


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    with Session() as session:
        app = QtWidgets.QApplication()
        window = Window(None, session)
        window.show()

        sys.exit(app.exec_())
