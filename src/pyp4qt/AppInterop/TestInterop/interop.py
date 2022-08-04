import os

from pyp4qt.version import __version__
from PySide2 import QtCore, QtGui, QtWidgets
from pyp4qt.AppInterop.BaseInterop import BaseInterop
from pyp4qt import utils


class TestInterop(BaseInterop):
    window = None

    @staticmethod
    def setupEnvironment():
        class TestWidget(QtWidgets.QWidget):
            def keyPressEvent(self, e):
                if e.key() == QtCore.Qt.Key_Escape:
                    self.close()

        app = QtWidgets.QApplication([])

        TestInterop.window = TestWidget()
        return TestInterop.window, app

    @staticmethod
    def main_parent_window():
        return TestInterop.window

    @staticmethod
    def getSettingsPath():
        cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        return cwd

    @staticmethod
    def getIconPath():
        cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        iconpath = os.path.join(cwd, "../Images/")
        return os.path.realpath(iconpath)

    @staticmethod
    def getSceneFiles():
        return ['.txt']

    @staticmethod
    def getTempPath():
        import tempfile
        return tempfile.gettempdir()

    @staticmethod
    def getCurrentSceneFile():
        import tempfile
        return tempfile.TemporaryFile().name

    @staticmethod
    def openScene(filePath):
        with open(filePath) as f:
            Utils.p4Logger().info(f.read())

    @staticmethod
    def closeWindow(ui):
        raise NotImplementedError

    @staticmethod
    def refresh():
        pass

    def initializeMenu(self, entries):
        window = TestInterop.window
        vbox = QtWidgets.QVBoxLayout()
        window.setLayout(vbox)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu = self.menu_bar.addMenu('Perforce')
        vbox.addWidget(self.menu_bar)

    def addMenuDivider(self, menu, label):
        self.menu.addSeparator()

    def addMenuLabel(self, menu, label):
        self.menu.addAction(label)

    def addMenuSubmenu(self, menu, label, icon, entries):
        # Save our current menu
        parent = self.menu
        self.menu = parent.addMenu(QtGui.QIcon(icon), label)

        # Fill up the submenu
        self.fillMenu(entries)

        # Reset our current menu
        self.menu = parent

    def addMenuCommand(self, menu, label, icon, command):
        self.menu.addAction(QtGui.QIcon(icon), label, command)
