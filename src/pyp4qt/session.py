# Project Modules


# Python Modules
import os
from P4 import P4, P4Exception


class DepotDirectory(object):
    def __init__(self):
        self.dir = None


class DepotFile(object):
    def __init__(self):
        self.depotFile = None
        self.rev = None
        self.change = None
        self.action = None
        self.type = None
        self.time = None


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
            obj = DepotDirectory()

            for key in item:
                setattr(obj, key, item[key])

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
            obj = DepotFile()

            for key in item:
                setattr(obj, key, item[key])

            result.append(obj)

        return result


if __name__ == "__main__":
    _test = Session()
    _test.connect()
    # print(_test.info())
    # print(_test.depot_dirs())
    print(_test.depot_files("//iw8-source"))
    # print(_test.run("files", "//iw8-source/*"))
    # print(_test.run("dirs", "//iw8-source/*"))
    _test.disconnect()
