# Project Modules
from pyp4qt.session import Session
from pyp4qt.qt.config_depot_model import ConfigDepotModel, ConfigDepotItem
from pyp4qt import globals

# Python Modules
import os
from PySide2.QtCore import Qt, Signal, QModelIndex
from PySide2.QtWidgets import QWidget, QSplitter, QTextEdit, QTreeView, QVBoxLayout, QLabel, \
    QAbstractItemView, QDialog, QDialogButtonBox


class ConfigDepotWidget(QWidget):
    selection_changed = Signal(QModelIndex)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self._items = list()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Model
        self._model = ConfigDepotModel(self)

        # View
        self._view = QTreeView(self)
        self._view.setModel(self._model)
        self._view.setAlternatingRowColors(True)
        self._view.setFocusPolicy(Qt.NoFocus)
        self._view.selectionModel().currentChanged.connect(self._on_current_changed)

        layout.addWidget(self._view)

    def set_session(self, session):
        self._model.setSession(session)
        return

    def set_config(self, path):
        self._model.setConfig(path)
        return

    def _on_current_changed(self, current, previous):
        if not current.isValid():
            self.selection_changed.emit(QModelIndex())
            return

        item = current.internalPointer()

        if item.type() not in [ConfigDepotItem.TYPE_FILE, ConfigDepotItem.TYPE_FILE_VERSION]:
            self.selection_changed.emit(QModelIndex())
            return

        self.selection_changed.emit(current)
        return

    def checkout(self):
        """ Checkouts the current selected indexes and returns the client paths

        Returns:
            str
        """
        indexes = self._view.selectionModel().selectedIndexes()

        client_file = str()

        if indexes:
            item = indexes[0].internalPointer()
            self._items = [item]

            if self._model.session():
                try:
                    client_file = self._model.session().checkout_file(item.path())
                except:
                    client_file = item.client_file()

            os.environ[globals.CURRENT_COMMENT] = item.comment()

        return client_file

    def open(self):
        """ Returns a client path of the current selected indexes

        Returns:
            str
        """
        indexes = self._view.selectionModel().selectedIndexes()

        client_file = str()

        if indexes:
            item = indexes[0].internalPointer()
            self._items = [item]

            client_file = item.client_file()

            os.environ[globals.CURRENT_COMMENT] = item.comment()

        return client_file

    def items(self):
        return self._items


class ConfigDepotDialog(QDialog):
    def __init__(self, parent=None, session=None, config=None):
        QDialog.__init__(self, parent)

        # Default
        self._session = session

        self.setWindowTitle("Depot Checkout")
        self.setModal(True)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Widget
        self.widget = ConfigDepotWidget(self)
        self.widget.set_session(session)
        self.widget.set_config(config)
        layout.addWidget(self.widget)

        self.widget.selection_changed.connect(self._on_selection_changed)

        # Buttons
        self._buttons = QDialogButtonBox()

        self._checkout_button = self._buttons.addButton("Checkout/Open", QDialogButtonBox.AcceptRole)
        self._checkout_button.setEnabled(False)

        self._checkout_button.clicked.connect(self._on_checkout)

        self._open_button = self._buttons.addButton(QDialogButtonBox.Open)
        self._open_button.setEnabled(False)

        self._open_button.clicked.connect(self._on_open)

        self._cancel_button = self._buttons.addButton(QDialogButtonBox.Cancel)

        layout.addWidget(self._buttons)

        # self._buttons.accepted.connect(self._do_accept)
        self._buttons.rejected.connect(self.reject)

    def _on_selection_changed(self, index):
        if not index.isValid():
            self._checkout_button.setEnabled(False)
            self._open_button.setEnabled(False)
            return

        self._checkout_button.setEnabled(True)
        self._open_button.setEnabled(True)

        return

    def _on_open(self):
        result = self.widget.open()

        if not result:
            raise RuntimeError("Nothing selected.")

        self.accept()
        return

    def _on_checkout(self):
        result = self.widget.checkout()

        if not result:
            raise RuntimeError("Nothing selected.")

        self.accept()
        return

    def items(self):
        return self.widget.items()


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication

    with Session() as session:
        app = QApplication()
        widget = ConfigDepotDialog(None,
                                   session,
                                   "")
        # widget.populate_files(session)
        if widget.exec_() == QDialog.Accepted:
            print(widget.items())
            sys.exit()
        else:
            sys.exit()
