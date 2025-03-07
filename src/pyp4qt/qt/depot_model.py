# Project Modules
import pyp4qt.utils
from pyp4qt.session import Session, DepotFile, DepotDirectory, P4Exception

# Python Modules
import os
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt


class DepotItem(object):
    TYPE_NONE = 0
    TYPE_DIR = 1
    TYPE_FILE = 2

    def __init__(self, session=None, parent=None, type=0, path=str()):
        self._session = session
        self._parent = parent
        self._path = path
        self._type = type
        self._children = list()
        self._is_loaded = False

    def type(self):
        return self._type

    def session(self):
        return self._session

    def set_session(self, session):
        self._session = session
        return

    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent
        return

    def path(self):
        return self._path

    def set_path(self, path):
        self._path = path
        return

    def data(self, index):
        """ Returns data by column index.

        Args:
            index (int)

        Returns:
            str
        """
        if index == 0:
            if self._path:
                path_split = self._path.split("/")
                return path_split[-1]
        return

    def load(self):
        """ Loads the children from the depot into memory.

        Returns:
            None
        """
        self._children = list()

        if not self._session or not self._path:
            self._is_loaded = False
            return

        # Get Directories
        try:
            for _dir in self._session.depot_dirs(self._path):
                dir_item = DepotItem(self._session, self, DepotItem.TYPE_DIR, _dir.dir)
                self._children.append(dir_item)
        except P4Exception:
            pass

        # Get Files
        try:
            for file in self._session.depot_files(self._path):
                file_item = DepotItem(self._session, self, DepotItem.TYPE_FILE, file.depotFile)
                self._children.append(file_item)
        except P4Exception:
            pass

        self._is_loaded = True
        return

    def isLoaded(self):
        return self._is_loaded

    def hasChildren(self):
        return self.childCount() > 0

    def child(self, index):
        try:
            return self._children[index]
        except IndexError:
            pass
        return None

    def children(self):
        return self._children

    def append_child(self, child):
        """ Append a child object.

        Args:
            child (DepotItem)

        Returns:
            None
        """
        if not isinstance(child, DepotItem):
            raise RuntimeError("Invalid child type.")

        child.set_parent(self)
        self._children.append(child)
        return

    def sessionChildCount(self):
        """ Returns the child count of children within the depot.

        Returns:
            int
        """
        if self._type != DepotItem.TYPE_DIR or not self._path or not self._session:
            return 0

        dirs = list()
        files = list()

        try:
            dirs = self._session.depot_dirs(self._path)
        except P4Exception:
            pass

        try:
            files = self._session.depot_files(self._path)
        except P4Exception:
            pass

        return len(dirs) + len(files)

    def childCount(self):
        if self._is_loaded:
            return len(self._children)

        return self.sessionChildCount()

    def row(self):
        if self._parent:
            return self._parent.children().index(self)

        return 0


class DepotModel(QAbstractItemModel):
    def __init__(self, parent=None, session=None):
        QAbstractItemModel.__init__(self, parent)

        self._session = session
        self._root = DepotItem(session, path="//*")

        if self._session:
            self._populate()

    def session(self):
        return self._session

    def setSession(self, session):
        self.clear()
        self._session = session
        self._populate()
        return

    def root(self):
        return self._root

    def clear(self):
        self.beginResetModel()
        self._session = None
        del (self._root)
        self._root = DepotItem(self._session, path="//*")
        self.endResetModel()
        return

    def _populate(self):
        self.beginResetModel()
        self._root.load()
        self.endResetModel()
        return

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())

        # elif role == Qt.CheckStateRole and index.column() == 0:
        #     return item.getCheckedState()

        return

    def itemFromIndex(self, index):
        """ Returns a pointer to a DepotItem from a QModelIndex.

        Args:
            index (QModelIndex)

        Returns:
            DepotItem
        """
        if not index.isValid():
            return None

        return index.internalPointer()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            item = self._root
        else:
            item = parent.internalPointer()

        return item.childCount()

    def canFetchMore(self, parent):
        """

        Args:
            index (QModelIndex)

        Returns:
            bool
        """
        if not parent.isValid():
            return False

        item = parent.internalPointer()

        if not item:
            return False

        return not item.isLoaded()

    def fetchMore(self, parent):
        item = parent.internalPointer()

        if item:
            self.beginInsertRows(parent, 0, item.childCount() - 1)
            item.load()
            self.endInsertRows()
        return

    def index(self, row, column, parent):
        """

        Args:
            row (int)
            column (int)
            parent (QModelIndex)

        Returns:
            QModelIndex
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            item = self._root
        else:
            item = parent.internalPointer()

        child = item.child(row)

        if child:
            return self.createIndex(row, column, child)

        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        parent_item = item.parent()

        if parent_item == self._root:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def hasChildren(self, parent):
        if not parent.isValid():
            item = self._root
        else:
            item = parent.internalPointer()

        return item.hasChildren()


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    app = QtWidgets.QApplication()
    session = Session()
    session.connect()

    view = QtWidgets.QTreeView()
    model = DepotModel(view, session)
    view.setModel(model)
    view.show()

    session.disconnect()
    sys.exit(app.exec_())
