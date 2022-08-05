import os
import logging
import sys
import platform

import nuke
    
import pyp4qt.globals
from pyp4qt import utils
from pyp4qt.version import __version__
from pyp4qt.adapter import Adapter
from pyp4qt.callbacks import Callbacks
from PySide2 import QtCore, QtGui, QtWidgets


class NukeAdapter(Adapter):
    @staticmethod
    def setup_env():
        pass

    @staticmethod
    def main_parent_window():
        return None
        # return QtWidgets.QApplication.activeWindow()
  
    @staticmethod
    def get_settings_path():
        if platform.system() == 'Windows':
            if os.environ.get('HOME'):
                home = os.environ['HOME']
            else:
                home = os.environ['USERPROFILE']
            return os.path.join(home, '.nuke')

        elif platform.system() == 'Linux':
            return os.path.expanduser('~/.nuke')

        elif platform.system() == 'Darwin':
            return os.path.expanduser('~/.nuke')

    @staticmethod
    def get_icons_path():
        return os.path.join(NukeAdapter.get_settings_path(), "P4Nuke", "perforce", "icons")
    
    @staticmethod
    def get_scene_files():
        return ['.nk']
    
    @staticmethod
    def get_temp_path():
        return os.environ['NUKE_TEMP_DIR']

    @staticmethod
    def get_current_scene_file():
        return nuke.root().name()


    @staticmethod
    def open_scene(filePath):
        nuke.scriptOpen(filePath)


    @staticmethod
    def close_window(ui):
        pass


    @staticmethod
    def refresh():
        nuke.updateUI()


    # Nuke doesn't like absolute icons for it's menus,
    # so strip out the filename only and ignore the path
    def sanitizeIconPath(self, iconPath):
        return os.path.basename(iconPath)
    
    def init_menu(self, entries):
        m = nuke.menu( 'Nuke' )
        self.menu = m.addMenu( 'Perforce' )

    def add_menu_divider(self, label):
        self.menu.addSeparator()
       
    def add_menu_label(self, label):
        tmp = self.menu.addCommand(label, lambda: None)
        tmp.setEnabled(False)

    def add_menu_submenu(self, label, iconPath, entries):
        # Save our current menu
        parent = self.menu
        self.menu = parent.addMenu(label, icon=self.sanitizeIconPath(iconPath))

        # Fill up the submenu
        self.fill_menu(entries)

        # Reset our current menu
        self.menu = parent


    def add_menu_command(self, label, iconPath, command):
        self.menu.addCommand(label, command, icon=self.sanitizeIconPath(iconPath))