import os
import logging
import sys
import platform

import hou
    
import pyp4qt.globals
from pyp4qt import utils
from pyp4qt.version import __version__
from pyp4qt.adapter import Adapter
from pyp4qt.callbacks import Callbacks
from PySide2 import QtCore, QtGui, QtWidgets


class HoudiniAdapter(Adapter):
    @staticmethod
    def setup_env():
        pass
        # class TestWidget(QtWidgets.QWidget):
        #     def keyPressEvent(self, e):
        #         if e.key() == QtCore.Qt.Key_Escape:
        #             self.close()

        # app = QtWidgets.QApplication([])

        # StandaloneAdapter.window = TestWidget()
        # return StandaloneAdapter.window, app

    @staticmethod
    def main_parent_window():
        return hou.ui.mainQtWindow()
  
    @staticmethod
    def get_settings_path():
        return os.getenv("HOUDINI_USER_PREF_DIR")

    @staticmethod
    def get_icons_path():
        return os.path.join(HoudiniAdapter.get_settings_path(), "scripts", "P4Houdini" "perforce", "icons")
    
    @staticmethod
    def get_scene_files():
        return ['.hip', '.hipnc']
    
    @staticmethod
    def get_temp_path():
        return os.environ["HOUDINI_TEMP_DIR"]

    @staticmethod
    def get_current_scene_file():
        return hou.hipFile.path()


    @staticmethod
    def open_scene(filePath):
        hou.hipFile.load(filePath)


    @staticmethod
    def close_window(ui):
        pass


    @staticmethod
    def refresh():
        pass


    def init_menu(self, entries):
        self.menu = QtWidgets.QMenu( hou.ui.mainQtWindow() )
        self.menu.setTitle('Perforce')

    def add_menu_divider(self, label):
        pass
        # self.menu.addSeparator()
       
    def add_menu_label(self, label):
        pass
        # tmp = self.menu.addCommand(label, lambda: None)
        # tmp.setEnabled(False)

    def add_menu_submenu(self, label, iconPath, entries):
        pass
        # # Save our current menu
        # parent = self.menu
        # self.menu = parent.addMenu(label, icon=self.sanitizeIconPath(iconPath))

        # # Fill up the submenu
        # self.fill_menu(entries)

        # # Reset our current menu
        # self.menu = parent


    def add_menu_command(self, label, iconPath, command):
        pass
        # self.menu.addCommand(label, command, icon=self.sanitizeIconPath(iconPath))