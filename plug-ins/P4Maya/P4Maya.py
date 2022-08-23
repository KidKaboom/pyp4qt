import pyp4qt
import pyp4qt.qt

import sys
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx

kPluginCmdName = "MayaP4Integration"
kMenuName = "PerforceMenu"

kPerforceWindowName = "PerforceWindow"
kChangelistWindowName = "PerforceChangelistWindow"
kDepotWindowName = "PerforceDepotWindow"

#FIXME: This is for demo / need to properly rework it.
class MayaP4Command(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, *args, **kwargs):
        print("P4Maya.py")

    @staticmethod
    def main_parent_window():
        """
        Get the main Maya window as a QtGui.QMainWindow instance
        @return: QtGui.QMainWindow instance of the top level Maya windows
        """
        from PySide2.QtWidgets import QWidget
        from shiboken2 import wrapInstance

        maya_pointer = OpenMayaUI.MQtUtil.mainWindow()
        maya_window = wrapInstance(int(maya_pointer), QWidget)
        return maya_window

    @staticmethod
    def init_ui(*args, **kwargs):
        window = None

        try:
            window = mel.eval('$temp1=$gMainWindow')
        except:
            pass

        if window:
            MayaP4Command.delete_ui()

            menu = cmds.menu(kMenuName, parent=window, tearOff=True, label='Perforce')
            cmds.menuItem(label="Perforce Window", command=MayaP4Command.show_perforce)
            cmds.menuItem(label="Depot / Workspace Window", command=MayaP4Command.show_depot)
            cmds.menuItem(divider=True)
            cmds.menuItem(label="New Changelist", command=MayaP4Command.show_changelist)
            cmds.menuItem(label="Submit Changelist", enable=False)
            cmds.menuItem(divider=True)
            cmds.menuItem(label="Sync", enable=False)
            cmds.setParent(menu, menu=True)
        return

    @staticmethod
    def delete_ui(*args, **kwargs):
        try:
            cmds.deleteUI(kMenuName, menu=True)
        except:
            pass

        for window in [kPerforceWindowName, kChangelistWindowName, kDepotWindowName]:
            try:
                cmds.deleteUI(window)
            except:
                pass
        return

    @staticmethod
    def show_perforce(*args, **kwargs):
        try:
            cmds.deleteUI(kPerforceWindowName)
        except:
            pass

        session = pyp4qt.Session()

        if not session.connected():
            session.connect()

        parent = MayaP4Command.main_parent_window()
        window = pyp4qt.qt.Window(parent, session)
        window.setObjectName(kPerforceWindowName)
        window.setWindowTitle("Perforce")
        window.show()
        return

    @staticmethod
    def show_depot(*args, **kwargs):
        try:
            cmds.deleteUI(kDepotWindowName)
        except:
            pass

        session = pyp4qt.Session()

        if not session.connected():
            session.connect()

        parent = MayaP4Command.main_parent_window()
        window = pyp4qt.qt.DepotWidget(parent, session)
        window.setObjectName(kDepotWindowName)
        window.setWindowTitle("Perforce Depot")
        window.show()
        return

    @staticmethod
    def show_changelist(*args, **kwargs):
        try:
            cmds.deleteUI(kChangelistWindowName)
        except:
            pass

        session = pyp4qt.Session()

        if not session.connected():
            session.connect()

        parent = MayaP4Command.main_parent_window()
        window = pyp4qt.qt.ChangeListDialog(parent, session)
        window.setObjectName(kChangelistWindowName)
        window.setWindowTitle("New Changelist")
        window.show()
        return


def cmdCreator():
    return OpenMayaMPx.asMPxPtr(MayaP4Command())

def initializePlugin(mobject):
    plugin = OpenMayaMPx.MFnPlugin(mobject, "Justin Tirado", "1.0.0", "Any")
    try:
        # print("Adding Perforce Menu")
        # pyp4qt.init()
        plugin.registerCommand(kPluginCmdName, cmdCreator)
        plugin.registerUI(MayaP4Command.init_ui, MayaP4Command.delete_ui)
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
        raise
    return


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    plugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        # print("Removing Perforce Menu")
        # pyp4qt.close()
        plugin.deregisterCommand(kPluginCmdName)
    except Exception as e:
        print(e)
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
    return
