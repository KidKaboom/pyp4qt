# Project Modules
import pyp4qt.utils
from pyp4qt.session import Session, P4Exception
from pyp4qt.qt.depot_model import DepotItem, DepotModel

# Python Modules
import os
import json
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide2.QtWidgets import QStyle, QApplication


class ConfigDepotItem(DepotItem):
    TYPE_CONFIG = 3
    TYPE_FILE_VERSION = 4

    @classmethod
    def from_dict(cls, session=None, parent=None, data=None):
        """ Return a ConfigDepotItem object from a dictionary.

        Args:
            session (Session)
            parent(ConfigDepotItem)
            data (dict)

        Returns:
            ConfigDepotItem
        """
        comment = str()

        if parent:
            comment = parent.comment() + data.get("comment", str())

        obj = cls(
            session=session,
            parent=parent,
            type=ConfigDepotItem.TYPE_CONFIG,
            name=data.get("name", str()),
            display_name=data.get("displayName", str()),
            path=data.get("path", str()),
            export_path=data.get("exportPath", str()),
            show_files=data.get("showFiles", False),
            show_dirs=data.get("showDirectories", False),
            comment=comment,
            description=data.get("description", str()),
            category=data.get("category", str())
        )

        children = data.get("children", list())

        if isinstance(children, (list, tuple)):
            for child in children:
                if isinstance(child, dict):
                    child_obj = cls.from_dict(session, obj, child)
                    obj.append_child(child_obj)

        return obj

    def __init__(self,
                 session=None,
                 parent=None,
                 type=0,
                 name=str(),
                 display_name=str(),
                 path=str(),
                 export_path=str(),
                 show_files=False,
                 show_dirs=False,
                 comment=str(),
                 description=str(),
                 category=str()
                 ):

        DepotItem.__init__(self, session, parent, type, path)

        # Config Attributes
        self._name = name
        self._display_name = display_name
        self._export_path = export_path
        self._show_files = show_files
        self._show_dirs = show_dirs
        self._comment = comment
        self._description = description
        self._category = category

        self._app = list()
        self._expand = False
        self._depot = False
        self._filter = str()
        self._recursive = False

        # Depot Attributes
        self._rev = None
        self._change = None
        self._action = None
        self._time = None

        self._client_file = None
        self._is_mapped = None
        self._head_action = None
        self._head_time = None
        self._head_rev = None
        self._head_change = None
        self._head_mod_time = None
        self._have_rev = None

        self._action_owner = None
        self._work_rev = None
        self._other_open = list()
        self._other_action = list()
        self._other_change = list()
        self._other_opens = None

        self._client = None
        self._user = None

    def isLoaded(self):
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            if not self.show_dirs() and not self.show_files():
                return True

        return DepotItem.isLoaded(self)

    def name(self):
        return self._name

    def display_name(self):
        if self._display_name:
            return self._display_name
        return self.name()

    def export_path(self):
        return self._export_path

    def show_files(self):
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            return self._show_files
        return False

    def show_dirs(self):
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            return self._show_dirs
        return False

    def comment(self):
        return self._comment

    def description(self):
        return self._description

    def category(self):
        return self._category

    def client_file(self):
        return self._client_file

    def data(self, index):
        """ Returns data by column index.

        Args:
            index (int)

        Returns:
            str
        """
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            if index == 0:
                return self.display_name()

        if self.type() in [ConfigDepotItem.TYPE_FILE, ConfigDepotItem.TYPE_FILE_VERSION]:
            if index == 1:
                if self._head_rev:
                    return self._head_rev

                return self._rev

            elif index == 2:
                if self._head_change:
                    return self._head_change

                return self._change

            elif index == 3:
                if self._user:
                    return self._user
                return self._action_owner

            elif index == 4:
                return self._description

        return DepotItem.data(self, index)

    def load(self):
        """ Loads the children from the depot into memory.

        Returns:
            None
        """
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            if not self.show_dirs() and not self.show_files():
                return

        # self._children = list()

        if not self._session or not self._path:
            self._is_loaded = False
            return

        # Get Directories
        if self.type() in [ConfigDepotItem.TYPE_DIR, ConfigDepotItem.TYPE_CONFIG]:
            try:
                for _dir in self._session.depot_dirs(self._path):
                    # dir_item = DepotItem(self._session, self, DepotItem.TYPE_DIR, _dir.dir)

                    dir_item = ConfigDepotItem(
                        session=self._session,
                        parent=self,
                        type=DepotItem.TYPE_DIR,
                        path=_dir.dir,
                        comment=self._comment
                    )

                    self._children.append(dir_item)
            except P4Exception:
                pass

            # Get Files
            try:
                for file in self._session.depot_files(self._path):
                    # file_item = DepotItem(self._session, self, DepotItem.TYPE_FILE, file.depotFile)
                    file_item = ConfigDepotItem(
                        session=self._session,
                        parent=self,
                        type=ConfigDepotItem.TYPE_FILE,
                        path=file.depotFile,
                        comment=self._comment
                    )

                    file_item._rev = int(file.rev)
                    file_item._change = int(file.change)
                    file_item._action = file.action
                    file_item._time = file.time

                    # Get Info
                    info = dict()
                    log = dict()

                    if self._session:
                        # info = self._session.file_info(file_item.path())
                        info = self._session.run("fstat", file_item.path())[0]
                        log = self._session.run("filelog", file_item.path())[0]

                    if info:
                        file_item._client_file = info.get("clientFile")
                        file_item._is_mapped = info.get("isMapped")
                        file_item._head_action = info.get("headAction")
                        file_item._head_time = int(info.get("headTime", 0))
                        file_item._head_rev = int(info.get("headRev", 0))
                        file_item._head_change = int(info.get("headChange", 0))
                        file_item._head_mod_time = int(info.get("headModTime", 0))
                        file_item._have_rev = int(info.get("haveRev", 0))
                        file_item._action_owner = info.get("actionOwner")
                        file_item._work_rev = int(info.get("workRev", 0))
                        file_item._other_open = info.get("otherOpen")
                        file_item._other_action = info.get("otherAction")
                        file_item._other_change = info.get("otherChange")
                        file_item._other_opens = int(info.get("otherOpens", 0))

                    if log:
                        i = file_item._head_rev - 1
                        file_item._user = log.get("user")[i]
                        file_item._description = log.get("desc")[i]

                    self.append_child(file_item)

            except P4Exception:
                pass

        elif self.type() == ConfigDepotItem.TYPE_FILE:
            # Get Versions
            log = dict()

            if self._session:
                # log = self.session().file_log(file_item.path())
                log = self._session.run("filelog", self.path())[0]

            if log:
                rev = log.get("rev", list())

                for i in range(len(rev)):
                    version_item = ConfigDepotItem(
                        session=self._session,
                        parent=self,
                        type=ConfigDepotItem.TYPE_FILE_VERSION,
                        path=self.path(),
                        comment=self._comment
                    )

                    version_item._rev = int(log.get("rev")[i])
                    version_item._change = int(log.get("change")[i])
                    version_item._action = log.get("action")[i]
                    version_item._time = int(log.get("time")[i])
                    version_item._user = log.get("user")[i]
                    version_item._client = log.get("client")[i]
                    version_item._description = log.get("desc")[i]

                    version_item._is_loaded = True

                    if version_item._rev != self._rev:
                        self.append_child(version_item)

        self._is_loaded = True
        return

    def childCount(self):
        if self.type() == ConfigDepotItem.TYPE_CONFIG:
            if not self.show_dirs() and not self.show_files():
                return len(self._children)

        elif self.type() == ConfigDepotItem.TYPE_FILE:
            if isinstance(self._rev, int):
                if self._rev == 1:
                    return 0

                elif self._rev > 1:
                    return self._rev

            return len(self.children())

        elif self.type() == ConfigDepotItem.TYPE_FILE_VERSION:
            return 0

        return DepotItem.childCount(self)

    def sessionChildCount(self):
        """ Returns the child count of children within the depot.

        Returns:
            int
        """
        if self.type() not in [ConfigDepotItem.TYPE_DIR, ConfigDepotItem.TYPE_CONFIG]:
            return 0

        if not self.path():
            return 0

        if not self.session():
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


class ConfigDepotModel(QAbstractItemModel):
    def __init__(self, parent=None, session=None, config=str()):
        QAbstractItemModel.__init__(self, parent)

        self._session = session
        self._config = config
        self._root = ConfigDepotItem(session, path="//*")


    def config(self):
        return self._config

    def session(self):
        return self._session

    def setSession(self, session):
        self._session = session
        return

    def root(self):
        return self._root

    def clear(self):
        self.beginResetModel()
        self._session = None
        del (self._root)
        self._root = ConfigDepotItem(self._session)
        self.endResetModel()
        return

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        item = index.internalPointer()

        if item.type() in [ConfigDepotItem.TYPE_DIR, ConfigDepotItem.TYPE_CONFIG]:
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())

        elif role == Qt.DecorationRole and index.column() == 0:
            result = QStyle.SP_FileIcon

            if item.type() == ConfigDepotItem.TYPE_CONFIG:
                result = QStyle.SP_DirLinkIcon

            elif item.type() == ConfigDepotItem.TYPE_DIR:
                result = QStyle.SP_DirIcon

            return QApplication.style().standardIcon(result)

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

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Version"
            elif section == 2:
                return "Changelist"
            elif section == 3:
                return "User"
            elif section == 4:
                return "Description"
        return None

    def columnCount(self, parent=QModelIndex()):
        return 5

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

    def setConfig(self, path):
        """ Set the model from a config file.

        Args:
            path (str)

        Returns:
            None
        """
        self._config = path

        if not self._config:
            return

        if not path.endswith(".json") or not os.path.isfile(path):
            raise RuntimeError("Must provide a valid .json file.")

        data = dict()

        with open(self._config) as _file:
            data = json.load(_file)

        # Check the schema?
        if data.get("name", str()) != "root":
            raise RuntimeError("File provided doesn't follow the proper schema.")

        # Check the Depot Path
        root_path = data.get("path", str())

        if not root_path or not self._session.is_valid_dir(root_path):
            raise RuntimeError("Path is not under client root.")

        # Update
        self.beginResetModel()
        self._root = ConfigDepotItem.from_dict(self._session, data=data)
        self.endResetModel()
        return


if __name__ == "__main__":
    import sys
    from PySide2 import QtWidgets

    with Session() as session:
        app = QtWidgets.QApplication()
        view = QtWidgets.QTreeView()
        model = ConfigDepotModel(view, session)
        model.setConfig("")
        view.setModel(model)
        view.show()

        sys.exit(app.exec_())
