import os
import logging
import sys
import platform

import Katana
from Katana import KatanaFile
import UI4
    
import pyp4qt.globals
from pyp4qt import utils
from pyp4qt.version import __version__
from pyp4qt.adapter import Adapter
from pyp4qt.callbacks import Callbacks
from PySide2 import QtCore, QtGui, QtWidgets


class KatanaAdapter(Adapter):
    @staticmethod
    def setup_env():
        pass

    @staticmethod
    def main_parent_window():
        return UI4.App.MainWindow.CurrentMainWindow()
        # return UI4.App.MainMenu.MainMenu.instance()
  
    @staticmethod
    def get_settings_path():
        user_dir = os.getenv("KATANA_USER_RESOURCE_DIRECTORY")
        if user_dir:
            return user_dir

        if platform.system() == 'Windows':
            if os.environ.get('HOME'):
                home = os.environ['HOME']
            else:
                home = os.environ['USERPROFILE']
            return os.path.join(home, '.katana')

        elif platform.system() == 'Linux':
            return os.path.expanduser('~/.katana')

        elif platform.system() == 'Darwin':
            return os.path.expanduser('~/.katana')

    @staticmethod
    def get_icons_path():
        return os.path.join(KatanaAdapter.get_settings_path(), "P4Katana", "perforce", "icons")
    
    @staticmethod
    def get_scene_files():
        return ['.katana']
    
    @staticmethod
    def get_temp_path():
        import tempfile
        return tempfile.gettempdir()

    @staticmethod
    def get_current_scene_file():
        pass


    @staticmethod
    def open_scene(filePath):
        KatanaFile.Load(filePath)


    @staticmethod
    def close_window(ui):
        pass


    @staticmethod
    def refresh():
        pass


    # Nuke doesn't like absolute icons for it's menus,
    # so strip out the filename only and ignore the path
    def sanitizeIconPath(self, iconPath):
        return os.path.basename(iconPath)

    def init_menu(self, entries):
        mainMenu = UI4.App.MainWindow.CurrentMainWindow().findChild(UI4.App.MainMenu.MainMenu)

        # Find help menu
        helpMenu = [action for action in mainMenu.actions() if action.text() == 'Help'][0]

        # Insert Perforce menu before the help menu
        self.menu = mainMenu.addMenu('Perforce')
        mainMenu.insertMenu(helpMenu, self.menu)

    def add_menu_divider(self, label):
        self.menu.addSeparator()
       
    def add_menu_label(self, label):
        self.menu.addAction(label)

    def add_menu_submenu(self, label, icon, entries):
        # Save our current menu
        parent = self.menu
        self.menu = parent.addMenu(QtGui.QIcon(icon), label)

        # Fill up the submenu
        self.fill_menu(entries)

        # Reset our current menu
        self.menu = parent


    def add_menu_command(self, label, icon, command):
        self.menu.addAction(QtGui.QIcon(icon), label, command)