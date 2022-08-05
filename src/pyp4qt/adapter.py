# Project Modules
from pyp4qt.version import __version__

# Python Modules
import tempfile


class Adapter(object):
    @staticmethod
    def setup_env():
        pass

    @staticmethod
    def main_parent_window():
        raise NotImplementedError

    @staticmethod
    def create_menu(entries):
        from pyp4qt.apps import interop

        # We need to import interop so the appropriate class is used while creating the menus
        interop = interop()
        interop.init_menu(entries)
        interop.fill_menu(entries)
        interop.add_menu_label("", "Version {0}".format(__version__))

    @staticmethod
    def get_settings_path():
        raise NotImplementedError

    @staticmethod
    def get_icons_path():
        raise NotImplementedError

    @staticmethod
    def get_scene_files():
        return []

    @staticmethod
    def get_temp_path():
        return tempfile.gettempdir()

    @staticmethod
    def get_current_scene_file():
        raise NotImplementedError

    @staticmethod
    def open_scene(filePath):
        raise NotImplementedError

    @staticmethod
    def close_window(ui):
        raise NotImplementedError

    @staticmethod
    def refresh():
        raise NotImplementedError

    def init_menu(self, entries):
        raise NotImplementedError

    def fill_menu(self, entries):
        for entry in entries:
            if entry.get('divider'):
                self.add_menu_divider("", entry.get('label'))
            elif entry.get('entries'):
                self.add_menu_submenu("", entry.get('label'), entry.get('image'), entry['entries'])
            elif entry.get('command'):
                self.add_menu_command("", entry.get('label'), entry.get('image'), entry.get('command'))
            else:
                raise ValueError('Unknown entry type for \'%s\'' % entry)

    def add_menu_divider(self, menu, label):
        raise NotImplementedError

    def add_menu_label(self, menu, label):
        raise NotImplementedError

    def add_menu_submenu(self, menu, label, icon, entries):
        raise NotImplementedError

    def add_menu_command(self, menu, label, icon, command):
        raise NotImplementedError
