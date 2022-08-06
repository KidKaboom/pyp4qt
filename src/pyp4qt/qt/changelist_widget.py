# Project Modules
from pyp4qt.session import Session
from pyp4qt.qt.pending_model import PendingModel

# Python Modules
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QSplitter, QTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel, \
    QAbstractItemView, QDialog, QDialogButtonBox


class ChangeListWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Splitter
        splitter = QSplitter()
        splitter.setOrientation(Qt.Vertical)
        layout.addWidget(splitter)

        # Description
        desc_widget = QWidget()
        desc_widget.setLayout(QVBoxLayout())
        desc_widget.layout().setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(desc_widget)

        desc_label = QLabel("Description:")
        desc_widget.layout().addWidget(desc_label)

        self._description = QTextEdit()
        self._description.setPlaceholderText("<enter description here>")
        self._description.setFocusPolicy(Qt.ClickFocus)
        desc_widget.layout().addWidget(self._description)

        # Files
        files_widget = QWidget()
        files_widget.setLayout(QVBoxLayout())
        files_widget.layout().setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(files_widget)

        files_label = QLabel("Files:")
        files_widget.layout().addWidget(files_label)

        self._table = QTableWidget()
        self._table.setFocusPolicy(Qt.ClickFocus)
        self._table.setColumnCount(2)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.verticalHeader().hide()
        self._table.setHorizontalHeaderLabels(["", "File"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 0)
        files_widget.layout().addWidget(self._table)

    def description(self):
        """ Returns the current description text.

        Returns:
            str
        """
        return self._description.text()

    def files(self):
        """ Returns a list of depot file paths from the table widget.

        Returns:
            list[str]
        """
        result = list()

        for row in range(self._table.rowCount()):
            checked = self._table.item(row, 0).checkState()
            file = self._table.item(row, 1).text()

            if checked == Qt.Checked:
                result.append(file)

        return result

    def populate_files(self, session):
        """ Populate the table widget from the default changelist.

        Args:
            session (Session)

        Returns:
            None
        """
        self._table.clearContents()

        if not session or not session.connected():
            return

        files = session.get_default_files()
        self._table.setRowCount(len(files))

        row = 0
        for file in files:
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check_item.setCheckState(Qt.Unchecked)
            self._table.setItem(row, 0, check_item)

            file_item = QTableWidgetItem(file.depotFile)
            self._table.setItem(row, 1, file_item)
            row += 1

        return


class ChangeListDialog(QDialog):
    def __init__(self, parent=None, session=None):
        QDialog.__init__(self, parent)

        # Default
        self._session = session

        self.setWindowTitle("Changlist Dialog")
        self.setModal(True)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Widget
        self.widget = ChangeListWidget(self)
        self.widget.populate_files(self._session)
        layout.addWidget(self.widget)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication

    with Session() as session:
        app = QApplication()
        widget = ChangeListDialog(None, session)
        # widget.populate_files(session)
        if widget.exec_() == QDialog.Accepted:
            print(widget.widget.files())
        # sys.exit(app.exec_())
