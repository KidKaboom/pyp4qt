# Python Modules
import os
from P4 import P4, P4Exception

# Qt Modules
from PySide2.QtCore import QObject, Signal, QThread


class DictStruct:
    """ Struct that can be constructed to and from a dictionary.
    """

    @classmethod
    def from_dict(cls, data):
        """ Constructs an object from a dictionary.

        Args:
            data (dict)

        Returns:
            DictStruct
        """
        if not isinstance(data, dict):
            raise RuntimeError("Must provide a dictionary.")

        obj = cls()

        for key in data.keys():
            if hasattr(obj, key):
                setattr(obj, key, data.get(key))

        return obj

    def to_dict(self):
        """ Returns a dictionary of class attributes.

        Returns:
            dict
        """
        return vars(self)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        return

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        return

    def __contains__(self, item):
        return hasattr(self, item)

    def __str__(self):
        result = "<" + self.__class__.__name__ + ": "
        result += str(vars(self))
        result += ">"
        return result

    def __repr__(self):
        return self.__str__()

    def get(self, key, default_value=None):
        if hasattr(self, key):
            return getattr(self, key)
        return default_value


class DepotDirectory(DictStruct):
    """ Struct that stores data for directories within the depot.
    """

    def __init__(self):
        self.dir = None


class DepotFile(DictStruct):
    """ Struct that stores data for files within the depot.
    """

    def __init__(self):
        self.depotFile = None
        self.rev = None
        self.change = None
        self.action = None
        self.type = None
        self.time = None
        self.haveRev = None
        self.client = None
        self.user = None
        self.clientFile = None


class ChangeList(DictStruct):
    """ Struct that stores data for change lists
    """

    def __init__(self):
        self.change = None
        self.time = None
        self.user = None
        self.client = None
        self.status = None
        self.changeType = None
        self.desc = None
        self.depotFile = list()
        self.action = list()
        self.type = list()
        self.rev = list()


class Session(P4):
    """ Subclass of a P4 Session with convenience methods.
    """

    def __del__(self):
        if self.connected():
            self.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connected():
            self.disconnect()
        return

    def info(self):
        """ Returns a dictionary of information from the current P4 session.

        Returns:
            dict()
        """
        result = dict()

        if not self.connected():
            return result

        info = self.run("info")

        if info:
            result = info[0]

        return result

    def user_name(self):
        """ Returns the string name of the user.

        Returns:
            str
        """
        return self.info().get("userName", str())

    def client_name(self):
        """ Returns the string name of the client

        Returns:
            str
        """
        return self.info().get("clientName", str())

    def client_root(self):
        """ Returns the current client root directory.

        Returns:
            str
        """
        return self.info().get("clientRoot", str())

    def last_user(self, path):
        """ Returns the name of the last user from a depot file path.

        Args:
            path (str)

        Returns:
            str
        """

        log = self.run("filelog", path)[0]
        users = log.get("user")

        if users:
            return users[0]

        return str()

    def has_user(self, path, user):
        """ Returns True if a user made modifications on depot file.

        Args:
            path (str)
            user (str)

        Returns:
            bool
        """
        log = self.run("filelog", path)[0]

        if user in log.get("user", list()):
            return True

        return False

    def depot_dirs(self, path=str(), recursive=False):
        """ Returns a list of DepotDirectory subdirectories from a root path.

        Args:
            path (str)
            recursive (bool)

        Returns:
            list[DepotDirectory]
        """
        result = list()

        if not self.connected():
            return result

        # Fix Path for querying
        if not path:
            path = "//*"
        else:
            if path.endswith("/"):
                path += "*"
            elif path.endswith("*"):
                pass
            else:
                path += "/*"

        # Get dirs
        query = self.run("dirs", path)

        for item in query:
            obj = DepotDirectory.from_dict(item)
            result.append(obj)

        return result

    def depot_files(self, path, recursive=False, extension_filter=None, user_filter=None):
        """ Returns a list of DepotFile files from a root path.

        Args:
            path (str)
            recursive (bool)
            extension_filter (list)
            user_filter (str)

        Returns:
            list[DepotFile]
        """
        result = list()

        if not self.connected():
            return result

        # Fix filter
        if isinstance(extension_filter, list):
            for i in range(len(extension_filter)):
                string = extension_filter[i]

                if isinstance(string, str) and not string.startswith("."):
                    extension_filter[i] = ".{}".format(string)

        # Fix Path for querying
        if recursive:
            if path.endswith("/"):
                path += "..."
            elif path.endswith("/..."):
                pass
            else:
                path += "/..."
        else:
            if path.endswith("/"):
                path += "*"
            elif path.endswith("/*"):
                pass
            else:
                path += "/*"

        # Get files
        if extension_filter and isinstance(extension_filter, list):
            for f in extension_filter:

                try:
                    query = self.run("files", "-e", path + f)
                except P4Exception:
                    return result

                if user_filter:
                    for item in query:
                        obj = DepotFile.from_dict(item)

                        if self.last_user(obj.depotFile) in user_filter:
                              result.append(DepotFile.from_dict(item))

                else:
                    result += [DepotFile.from_dict(item) for item in query]
        else:
            try:
                query = self.run("files", "-e", path)
            except:
                return result

            if user_filter:
                for item in query:
                    obj = DepotFile.from_dict(item)

                    if self.last_user(obj.depotFile) in user_filter:
                        result.append(DepotFile.from_dict(item))
            else:
                result = [DepotFile.from_dict(item) for item in query]

        return result

    def create_changelist(self, description):
        """ Create a new changelist and returns its id. Returns -1 if unable to create a new changelist.

        Args:
            description (str)

        Returns:
            int
        """
        if not self.connected():
            return -1

        result = self.save_change({"Change": "new", "Description": description})[0]
        return int(result.split()[1])

    def pending_changelists(self):
        """ Returns a list of pending change lists.

        Returns:
            list[Changelist]
        """
        result = list()

        if not self.connected():
            return result

        info = self.info()
        query = self.run_changes("-s", "pending", "-u", self.user_name())

        for item in query:
            if item.get("user") == info.get("userName") and item.get("client") == info.get("clientName"):
                changelist = ChangeList.from_dict(item)
                result.append(changelist)

        return result

    def revert_file(self, path):
        """ Revert the file from its path.

        Args:
            path (str)

        Returns:
            None
        """
        if not self.connected():
            return

        self.run("revert", "-a", path)
        return

    def checkout_file(self, path, changelist="default"):
        """ Checkout a file from its depot path and return its local path.

        Args:
            path (str)
            changelist (str, int)

        Returns:
            str
        """
        if not self.connected():
            return

        result = self.run("edit", "-c", changelist, path)[0]

        if isinstance(result, str):
            raise P4Exception(result)

        return result.get("clientFile", str())

    def move_to_changelist(self, path, changelist="default"):
        """ Move the file path to the provided changelist.

        Args:
            path (str)
            changelist (str, int)

        Returns:
            None
        """
        if not self.connected():
            return

        self.run("reopen", "-c", changelist, path)
        return

    def delete_changelist(self, changelist):
        """ Deletes the changelist

        Args:
            changelist (int)

        Returns:
            None
        """
        if not self.connected():
            return

        self.run("change", "-d", changelist)
        return

    def revert_changelist(self, changelist):
        """

        Args:
            changelist (int)

        Returns:
            None
        """
        if not self.connected():
            return

        self.run("revert", "-a", "-c", changelist)
        return

    def edit_changelist_description(self, changelist, description):
        """ Edit the change list's description.

        Args:
            changelist (int)
            description (str)

        Returns:
            None
        """

        if not self.connected():
            return

        data = self.fetch_change(changelist)
        data["Description"] = description

        self.save_change(data)
        return

    def submit_changelist(self, changelist):
        """ Submit the specified changelist

        Args:
            changelist (int)

        Returns:
            None
        """
        raise NotImplemented

    def get_changelist(self, changelist):
        """ Returns a Changelist object from a change list id.

        Args:
            changelist (str, int)

        Returns:
            ChangeList
        """
        result = list()

        if not self.connected():
            return result

        result = self.run("describe", changelist)[0]
        return ChangeList.from_dict(result)

    def get_default_files(self):
        """ Returns a list of DepotFiles with the "default" change list.

        Returns:
            list[DepotFile]
        """
        result = list()

        if not self.connected():
            return result

        for item in self.run("opened"):
            file = DepotFile.from_dict(item)
            result.append(file)

        return result

    def workspaces(self):
        """ Returns a list of workspace strings.

        Returns:
            list[str]
        """
        result = list()

        if not self.connected():
            return result

        data = self.run("clients", "-u", self.user_name())

        for item in data:
            workspace = item.get("client")

            if workspace:
                result.append(workspace)

        return result

    def file_info(self, path):
        """ Returns a dictionary of metadata from a depot file path.

        Args:
            path (str)

        Returns:
            dict
        """
        data = dict()

        if not self.connected():
            return data

        data = self.run("fstat", path)[0]

        return data

    def file_log(self, path):
        """ Returns a dictionary of file log metadata from a depot file path.

        Args:
            path (str)

        Returns:
            dict
        """
        data = dict()

        if not self.connected():
            return data

        try:
            data = _test.run("filelog", path)[0]
        except:
            pass

        return data

    def is_valid_dir(self, path):
        """ Returns True if the directory is within the client's root.

        Args:
            path (str)

        Returns:
            bool
        """
        # Fix Path
        if path.endswith("/..."):
            pass
        elif path.endswith("/"):
            path += "..."
        elif path.endswith("..."):
            pass
        else:
            path += "/..."

        result = False

        try:
            result = True if self.run("where", path) else False

        except:
            pass

        return result


class SessionCollectionWorker(QObject):
    """ Class that handles collection of directories, files, or changelists within a QThread.

    Examples:
        def slot(item):
            print(item.to_dict())

        thread = QThread()
        worker = SessionCollectionWorker(
                session=session,
                type=SessionCollectWorker.TYPE_FILE,
                path=path,
                recursive=True
                )

        worker.moveToThread(thread)
        worker.connectToThread(thread)
        worker.resultReady.connect(slot)
        thread.start()
    """

    TYPE_NONE = 0
    TYPE_DIR = 1
    TYPE_FILE = 2
    TYPE_DIR_FILE = 3
    TYPE_CHANGELIST = 4

    resultReady = Signal(DictStruct)
    workFinished = Signal()
    workFailed = Signal()

    progressTotalChanged = Signal(int)
    progressChanged = Signal(int)

    statusChanged = Signal(str)

    def __init__(self,
                 session,
                 type=0,
                 path=None,
                 recursive=False,
                 extension_filter=None,
                 user_filter=None
                 ):

        QObject.__init__(self)

        self._session = session
        self._type = type
        self._path = path
        self._recursive = recursive
        self._extension_filter = extension_filter
        self._user_filer = user_filter

        if extension_filter is None:
            self._extension_filter = list()

        if user_filter is None:
            self._user_filer = list()

    def connectToThread(self, targetThread):
        """ Convenience method of connecting this worker's signals and slots to a QThread it will be moved to.

        Args:
            targetThread (QThread)

        Returns:
            None
        """
        targetThread.started.connect(self.doWork)
        targetThread.finished.connect(self.deleteLater)

        self.workFinished.connect(targetThread.quit)
        self.workFailed.connect(targetThread.quit)
        return

    def doWork(self):
        """ Expensive operation that's handled within the QThread.

        Returns:
            None
        """
        # if not self._session:
        #     self.work_failed.emit()
        #     self.work_finished.emit()
        #     return

        if not self._session.connected():
            self.statusChanged.emit("Session is not connected.")
            self.workFailed.emit()
            return

        if self._type == self.TYPE_NONE:
            self.statusChanged.emit("Type is None.")
            self.workFailed.emit()
            return

        if self._type != self.TYPE_CHANGELIST and not self._path:
            self.statusChanged.emit("Does not have a path set.")
            self.workFailed.emit()
            return

        total = 0
        result = list()

        if self._type in [self.TYPE_DIR, self.TYPE_DIR_FILE]:
            self.statusChanged.emit("Retrieving directories from depot: " + self._path)
            dirs = self._session.depot_dirs(path=self._path, recursive=self._recursive)
            result += dirs
            total += len(dirs) - 1

        if self._type in [self.TYPE_FILE, self.TYPE_DIR_FILE]:
            self.statusChanged.emit("Retrieving files from depot: " + self._path)
            files = self._session.depot_files(path=self._path, recursive=self._recursive, extension_filter=self._extension_filter)
            result += files
            total += len(files) - 1

        if self._type == self.TYPE_CHANGELIST:
            self.statusChanged.emit("Retrieving pending changelists.")
            changelist = self._session.pending_changelists()
            result = changelist
            total = len(changelist) - 1

        self.progressTotalChanged.emit(total)

        for i in range(total):
            self.resultReady.emit(result[i])
            self.progressChanged.emit(i)

        self._session.disconnect()
        self.workFinished.emit()
        return


if __name__ == "__main__":
    _test = Session()
    _test.connect()
    _test.disconnect()