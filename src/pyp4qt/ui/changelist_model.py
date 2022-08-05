# Project Modules
from pyp4qt.session import Session, DepotFile, DepotDirectory, P4Exception

# Python Modules
import os
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt


class ChangeListItem(object):
    TYPE_NONE = 0
    TYPE_ROOT = 1
    TYPE_CHANGELIST = 2
    TYPE_FILE = 3

    def __init__(self, parent=None, _type=0, path=str(), description=str()):
        self._parent = parent
        self._type = _type
        self._path = path
        self._description = description
        self._children = list()
        self._is_loaded = False

    def parent(self):
        return self._parent

    def type(self):
        return self._type

    def path(self):
        return self._path

    def isLoaded(self):
        return self._is_loaded

    def children(self):
        return self._children

    def child(self, index):
        try:
            return self._children[index]
        except IndexError:
            pass
        return None

    def childCount(self):
        return len(self._children)

    def hasChildren(self, session=None):
        """ Returns True if the item has any children.

        Args:
            session (Session)

        Returns:
            bool
        """
        if self._is_loaded:
            return self.childCount() > 0

        if not session:
            return False

        if not session.connected():
            return False

        if self._type == ChangeListItem.TYPE_ROOT:
            return len(session.pending_changelists()) > 0

        elif self._type == ChangeListItem.TYPE_CHANGELIST and self._path:
            data = session.get_changelist(int(self._path))
            return len(data.depotFile) > 0

        return False

    def row(self):
        if self._parent:
            return self._parent.children().index(self)

        return 0

    def data(self, index):
        if index == 0:
            return self._path
        elif index == 1:
            return self._description
        return

    def load(self, session):
        """

        Args:
            session (Session)

        Returns:
            None
        """
        self._is_loaded = True

        if not session.connected():
            return

        # Update Root
        if self._type == ChangeListItem.TYPE_ROOT:

            # Get Change lists
            for item in session.pending_changelists():
                changelist_item = ChangeListItem(self, ChangeListItem.TYPE_CHANGELIST, item.change, item.desc.strip())

                self._children.append(changelist_item)

        # Update Changelist
        elif self._type == ChangeListItem.TYPE_CHANGELIST:

            info = session.get_changelist(self._path)

            for file in info.depotFile:
                file_item = ChangeListItem(self, ChangeListItem.TYPE_FILE, file)
                self._children.append(file_item)
        return


class ChangeListModel(QAbstractItemModel):
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)

        self._session = session
        self._root = ChangeListItem(_type=ChangeListItem.TYPE_ROOT)

    def isValid(self):
        """ Returns if the current session is valid and is connected.

        Returns:
            bool
        """
        return self._session and self._session.connected()

    def root(self):
        return self._root

    def clear(self):
        self.beginResetModel()
        self._session = None
        del (self._root)
        self._root = ChangeListItem(_type=ChangeListItem.TYPE_ROOT)
        self.endResetModel()
        return

    def session(self):
        return self._session

    def setSession(self, session):
        self.clear()
        self._session = session
        self._populate()
        return

    def _populate(self):
        if not self.isValid():
            return

        self.beginResetModel()
        self._root.load(self._session)
        self.endResetModel()
        return

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Change"
            elif section == 1:
                return "Description"
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())

        return

    def columnCount(self, parent=QModelIndex()):
        return 2

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
            item.load(self._session)
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

        return item.hasChildren(self._session)


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    with Session() as session:
        app = QtWidgets.QApplication()
        view = QtWidgets.QTreeView()
        model = ChangeListModel(view)
        model.setSession(session)
        view.setModel(model)
        view.show()

        sys.exit(app.exec_())
