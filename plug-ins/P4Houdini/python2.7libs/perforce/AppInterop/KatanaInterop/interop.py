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
from pyp4qt.apps.base_adapter import BaseAdapter, BaseCallbacks
from pyp4qt.qt.qtpy import QtCore, QtGui, QtWidgets


class KatanaAdapter(BaseAdapter):
    @staticmethod
    def setupEnvironment():
        pass

    @staticmethod
    def main_parent_window():
        return UI4.App.MainWindow.CurrentMainWindow()
        # return UI4.App.MainMenu.MainMenu.instance()
  
    @staticmethod
    def getSettingsPath():
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
    def getIconPath():
        return os.path.join(KatanaAdapter.getSettingsPath(), "P4Katana", "perforce", "icons")
    
    @staticmethod
    def getSceneFiles():
        return ['.katana']
    
    @staticmethod
    def getTempPath():
        import tempfile
        return tempfile.gettempdir()

    @staticmethod
    def getCurrentSceneFile():
        pass


    @staticmethod
    def openScene(filePath):
        KatanaFile.Load(filePath)


    @staticmethod
    def closeWindow(ui):
        pass


    @staticmethod
    def refresh():
        pass


    # Nuke doesn't like absolute icons for it's menus,
    # so strip out the filename only and ignore the path
    def sanitizeIconPath(self, iconPath):
        return os.path.basename(iconPath)

    def initializeMenu(self, entries):
        mainMenu = UI4.App.MainWindow.CurrentMainWindow().findChild(UI4.App.MainMenu.MainMenu)

        # Find help menu
        helpMenu = [action for action in mainMenu.actions() if action.text() == 'Help'][0]

        # Insert Perforce menu before the help menu
        self.menu = mainMenu.addMenu('Perforce')
        mainMenu.insertMenu(helpMenu, self.menu)

    def addMenuDivider(self, label):
        self.menu.addSeparator()
       
    def addMenuLabel(self, label):
        self.menu.addAction(label)

    def addMenuSubmenu(self, label, icon, entries):
        # Save our current menu
        parent = self.menu
        self.menu = parent.addMenu(QtGui.QIcon(icon), label)

        # Fill up the submenu
        self.fillMenu(entries)

        # Reset our current menu
        self.menu = parent


    def addMenuCommand(self, label, icon, command):
        self.menu.addAction(QtGui.QIcon(icon), label, command)