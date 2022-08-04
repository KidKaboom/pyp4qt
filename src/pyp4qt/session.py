# Project Modules


# Python Modules
import os
from P4 import P4, P4Exception

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


class Session(P4):
    """ Subclass of a P4 Session with convenience methods.
    """

    def __init__(self, *args, **kwargs):
        P4.__init__(self, *args, **kwargs)

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

    def depot_dirs(self, root=str()):
        """ Returns a list of DepotDirectory subdirectories from a root path.

        Args:
            root (str)

        Returns:
            list[DepotDirectory]
        """
        result = list()

        if not self.connected():
            return result

        # Fix Path for querying
        if not root:
            root = "//*"
        else:
            if root.endswith("/"):
                root += "*"
            elif root.endswith("*"):
                pass
            else:
                root += "/*"

        # Get dirs
        query = self.run("dirs", root)

        for item in query:
            obj = DepotDirectory.from_dict(item)
            result.append(obj)

        return result

    def depot_files(self, root):
        """ Returns a list of DepotFile files from a root path.

        Args:
            root (str)

        Returns:
            list[DepotFile]
        """
        result = list()

        if not self.connected():
            return result

        # Fix Path for querying
        if root.endswith("/"):
            root += "*"
        elif root.endswith("*"):
            pass
        else:
            root += "/*"

        # Get files
        query = self.run("files", root)

        for item in query:
            obj = DepotFile.from_dict(item)
            result.append(obj)

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


if __name__ == "__main__":
    _test = Session()
    _test.connect()
    # print(_test.info())
    # print(_test.depot_dirs())
    # print(_test.depot_files("//iw8-source"))
    # print(_test.run("files", "//iw8-source/*"))
    # print(_test.run("dirs", "//iw8-source/*"))
    # cl = _test.save_change({"Change": "new", "Description": "Test"})
    # print(cl)
    # print(_test.run_changes("-s", "pending", "-u", "jtirado"))
    # print(_test.pending_changelists()[0].desc)
    # print(_test.create_changelist("Test4"))
    # _test.edit_changelist(12118125, "Test3")
    _test.disconnect()
