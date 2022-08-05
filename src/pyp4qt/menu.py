# Project Modules
from pyp4qt import globals

# Python Modules
import os
import re
import json
from configparser import ConfigParser


class MenuItem:
    """ Struct that stores menu item information within a hierarchy.

    Attributes:
        name (str)
        displayName (str)
        description (str)
        command (None, str, function)
    """
    TYPE_NONE = 0
    TYPE_SECTION = 1
    TYPE_ITEM = 2
    TYPE_DIVIDER = 3
    TYPE_SUBMENU = 4

    @classmethod
    def from_dict(cls, data):
        """ Returns a menu item from a dictionary.

        Args:
            data (dict)

        Returns:
            MenuItem
        """
        obj = cls()

        # Update Object
        for key in data.keys():
            if hasattr(obj, key):
                setattr(obj, key, data[key])

        return obj

    @classmethod
    def from_str(cls, string):
        """ Returns a menu item from a formatted string.

        Args:
            string:

        Returns:
            MenuItem
        """
        raise NotImplemented

    def __init__(self, _type=0, name=str(), displayName=str(), icon=str(), description=str(), command=None):
        self.type = _type
        self.name = name
        self.displayName = displayName
        self.icon = icon
        self.description = description
        self.command = command

        self._children = list()

    def __len__(self):
        return len(self._children)

    def __getitem__(self, item):
        return self._children[item]

    def is_valid(self):
        """ Returns True if the item is valid by its type.

        Returns:
            bool
        """
        if self.type == self.TYPE_SECTION or self.type == self.TYPE_SUBMENU:
            if len(self._children) > 0:
                return True

        elif self.type == self.TYPE_ITEM:
            if self.name and self.command:
                return True

        elif self.type == self.TYPE_DIVIDER:
            return True

        return False


class Menu:
    """ Class that reads a config file and stores the menu's item data.
    """

    @staticmethod
    def config():
        """ Returns the path of the menu config file.

        Returns:
            str
        """
        return globals.MENU_CONFIG_FILE

    @staticmethod
    def read(path):
        """ Returns a list of MenuItems from a config file.

        Args:
            path (str)

        Returns:
            list[MenuItem]
        """
        if not os.path.isfile(path):
            raise RuntimeError("File path doesn't exist: '{}'".format(path))

        if not path.endswith(".ini"):
            raise RuntimeError("File is invalid: '{}'".format(path))

        config = ConfigParser()
        config.read(path)

        result = list()

        for section in config.sections():
            section_item = MenuItem(MenuItem.TYPE_SECTION, section)

            for option in config.options(section):
                value = config.get(section, option)

                if "{" in value:
                    item = MenuItem.from_dict(json.loads(value))
                else:
                    item = MenuItem()

                item.name = option
                item.type = MenuItem.TYPE_ITEM
                section_item._children.append(item)

            result.append(section_item)

        return result

    def __init__(self, path):
        self._path = path
        self._items = list()

        if self._path:
            self._items = self.read(self._path)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def path(self):
        return self._path

    def items(self):
        return self._items


if __name__ == "__main__":
    _test = Menu(Menu.config())
    print(_test[0].is_valid())
