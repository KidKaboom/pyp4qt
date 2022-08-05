import os

from pyp4qt.version import __version__
from PySide2 import QtCore, QtGui, QtWidgets
from pyp4qt.adapter import Adapter
from pyp4qt import utils


class StandaloneAdapter(Adapter):
    window = None

    @staticmethod
    def setup_env():
        class TestWidget(QtWidgets.QWidget):
            def keyPressEvent(self, e):
                if e.key() == QtCore.Qt.Key_Escape:
                    self.close()

        app = QtWidgets.QApplication([])

        StandaloneAdapter.window = TestWidget()
        return StandaloneAdapter.window, app

    @staticmethod
    def main_parent_window():
        return StandaloneAdapter.window

    @staticmethod
    def get_settings_path():
        cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        return cwd

    @staticmethod
    def get_icons_path():
        cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        iconpath = os.path.join(cwd, "../icons/")
        return os.path.realpath(iconpath)

    @staticmethod
    def get_scene_files():
        return ['.txt']

    @staticmethod
    def get_temp_path():
        import tempfile
        return tempfile.gettempdir()

    @staticmethod
    def get_current_scene_file():
        import tempfile
        return tempfile.TemporaryFile().name

    @staticmethod
    def open_scene(filePath):
        with open(filePath) as f:
            utils.logger().info(f.read())

    @staticmethod
    def close_window(ui):
        raise NotImplementedError

    @staticmethod
    def refresh():
        pass

    def init_menu(self, entries):
        window = StandaloneAdapter.window
        vbox = QtWidgets.QVBoxLayout()
        window.setLayout(vbox)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu = self.menu_bar.addMenu('Perforce')
        vbox.addWidget(self.menu_bar)

    def add_menu_divider(self, menu, label):
        self.menu.addSeparator()

    def add_menu_label(self, menu, label):
        self.menu.addAction(label)

    def add_menu_submenu(self, menu, label, icon, entries):
        # Save our current menu
        parent = self.menu
        self.menu = parent.addMenu(QtGui.QIcon(icon), label)

        # Fill up the submenu
        self.fill_menu(entries)

        # Reset our current menu
        self.menu = parent

    def add_menu_command(self, menu, label, icon, command):
        self.menu.addAction(QtGui.QIcon(icon), label, command)
