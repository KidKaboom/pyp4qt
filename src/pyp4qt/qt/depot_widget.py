# Project Modules
from pyp4qt.session import Session
from pyp4qt.qt.depot_model import DepotModel
from pyp4qt.qt.workspace_combobox import WorkspaceCombobox

# Python Modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QFileSystemModel, QTreeView, QAction, QMenu


class DepotWidget(QWidget):
    def __init__(self, parent=None, session=None):
        QWidget.__init__(self, parent)

        self._session = session
        self._info = dict()

        if self._session:
            self._info = self._session.info()

        # Layout
        self.setLayout(QVBoxLayout())
        # self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Workspace
        self._workspace = WorkspaceCombobox(self, self._session)
        self.layout().addWidget(self._workspace)

        # Tab
        self._tab = QTabWidget()
        self.layout().addWidget(self._tab)

        # Depot Model / View
        self._depot_model = DepotModel(self, self._session)
        self._depot_view = QTreeView(self)
        self._depot_view.setHeaderHidden(True)
        self._depot_view.setModel(self._depot_model)
        self._tab.addTab(self._depot_view, "Depot")

        self._depot_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._depot_view.customContextMenuRequested.connect(self._depot_context_menu)

        # Workspace Model / View
        self._workspace_model = QFileSystemModel()
        self._workspace_view = QTreeView()
        self._workspace_view.setHeaderHidden(True)
        self._workspace_view.setModel(self._workspace_model)

        for column in range(1, self._workspace_model.columnCount()):
            self._workspace_view.setColumnHidden(column, True)

        client_root = self._info.get("clientRoot")

        if client_root:
            index = self._workspace_model.setRootPath(client_root)
            self._workspace_view.setRootIndex(index)

        self._tab.addTab(self._workspace_view, "Workspace")

    def _depot_context_menu(self, point):
        index = self._depot_view.indexAt(point)
        item = index.internalPointer()

        if index.isValid():
            menu = QMenu()
            action = menu.addAction("Test")
            menu.exec_(self._depot_view.mapToGlobal(point))

        return


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    with Session() as session:
        app = QtWidgets.QApplication()
        widget = DepotWidget(None, session)
        widget.show()

        sys.exit(app.exec_())
