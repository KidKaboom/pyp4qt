import os
import logging
import sys

try:
    import maya.standalone

    maya.standalone.initialize()
except:
    pass

import maya.mel as mel
# import maya.utils as mu
import maya.cmds as cmds
import maya.OpenMayaUI as omui

try:
    from shiboken import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

import maya.OpenMaya as api

from pyp4qt.version import __version__
from pyp4qt.adapter import Adapter, BaseCallbacks
from pyp4qt.apps.MayaAdapter import utils
from pyp4qt import globals
from PySide2 import QtCore, QtGui, QtWidgets

CONTACT_ROOT = "CONTACTROOT"
REFERENCE_CALLBACK = None
SAVE_CALLBACK = None


class MayaCallbacks(BaseCallbacks):
    @staticmethod
    def validateSubmit():
        print("Validating submission")
        return 0

    @staticmethod
    def cleanupCallbacks():
        if REFERENCE_CALLBACK:
            try:
                api.MCommandMessage.removeCallback(REFERENCE_CALLBACK)
            except RuntimeError as e:
                print(e)

        if SAVE_CALLBACK:
            try:
                api.MCommandMessage.removeCallback(SAVE_CALLBACK)
            except RuntimeError as e:
                print(e)

    @staticmethod
    def initCallbacks():
        global REFERENCE_CALLBACK
        global SAVE_CALLBACK

        MayaCallbacks.cleanupCallbacks()

        REFERENCE_CALLBACK = api.MSceneMessage.addCheckFileCallback(
            api.MSceneMessage.kBeforeCreateReferenceCheck,
            MayaCallbacks.referenceCallbackFunc)

        SAVE_CALLBACK = api.MSceneMessage.addCallback(
            api.MSceneMessage.kAfterSave,
            MayaCallbacks.saveCallbackFunc)

    @staticmethod
    def saveCallbackFunc(*args):
        fileName = cmds.file(q=True, sceneName=True)

        if ".ma" in fileName:
            print("Save callback: Checking file {0} for education flags".format(fileName))
            utils.removeStudentTag(fileName)

    @staticmethod
    def referenceCallbackFunc(inputBool, inputFile, *args):
        api.MScriptUtil.getBool(inputBool)

        print("Reference callback: Checking file {0}".format(os.environ[CONTACT_ROOT]))

        try:
            contactrootpath = os.environ[CONTACT_ROOT]
        except KeyError as e:
            print("Error", e)
            api.MScriptUtil.setBool(inputBool, True)
            return

        rawpath = inputFile.rawPath()
        rawname = inputFile.rawName()
        oldpath = rawpath

        if contactrootpath in rawpath:
            rawpath = rawpath.replace(
                contactrootpath, "${0}".format(CONTACT_ROOT))
            inputFile.setRawPath(rawpath)
            print("Remapped {0} -> {1}".format(oldpath, rawpath))

        if CONTACT_ROOT in rawpath:
            resolvedName = os.path.join(rawpath.replace("${0}".format(CONTACT_ROOT), contactrootpath), rawname)
            print(rawpath, "->", resolvedName)
            inputFile.overrideResolvedFullName(resolvedName)

        # print "RAWPATH", inputFile.rawPath()
        # print "RAWFULLNAME", inputFile.rawFullName()
        # print "RAWEXPANDEDPATH", inputFile.expandedPath()

        api.MScriptUtil.setBool(inputBool, True)


class MayaAdapter(Adapter):
    @staticmethod
    def setupEnvironment():
        import maya.standalone
        maya.standalone.initialize("Python")

    @staticmethod
    def main_parent_window():
        """
        Get the main Maya window as a QtGui.QMainWindow instance
        @return: QtGui.QMainWindow instance of the top level Maya windows
        """

        import maya.OpenMayaUI as apiUI
        try:
            import shiboken2 as shiboken
        except:
            import shiboken

        ptr = apiUI.MQtUtil.mainWindow()

        if ptr is not None:
            return shiboken.wrapInstance(int(ptr), QtWidgets.QWidget)

    @staticmethod
    def getSettingsPath():
        return os.environ['MAYA_APP_DIR']

    @staticmethod
    def getIconPath():
        # return os.environ['MAYA_APP_DIR'] + "/scripts/Perforce/icons/"
        return globals.ICONS_DIR

    @staticmethod
    def getSceneFiles():
        return ['.ma', '.mb']

    @staticmethod
    def getTempPath():
        return os.environ['TMPDIR']

    @staticmethod
    def getCurrentSceneFile():
        return cmds.file(q=True, sceneName=True)

    @staticmethod
    def openScene(filePath):
        cmds.file(filePath, f=True, o=True)

    @staticmethod
    def closeWindow(ui):
        cmds.deleteUI(ui)

    @staticmethod
    def refresh():
        cmds.refresh()

    def initializeMenu(self, entries):
        try:
            # gMainWindow = MayaAdapter.main_parent_window()
            gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
        except RuntimeError as e:
            print(e)
            print('Are you running in Batch Python?')
            gMainWindow = None

        try:
            print('Initialising menu...')
            self.perforceMenu = cmds.menu("PerforceMenu", parent=gMainWindow, tearOff=True, label='Perforce')
            cmds.setParent(self.perforceMenu, menu=True)
        except RuntimeError as e:
            print('Maya error while trying to create menu:', )
            print(e)

    def addMenuDivider(self, menu, label):
        try:
            cmds.menuItem(divider=True, label=label)
        except RuntimeError as e:
            print('Maya error while trying to create divider:', )
            print(e)

    def addMenuLabel(self, menu, label):
        try:
            cmds.menuItem(label=label, en=False)
        except RuntimeError as e:
            print('Maya error while trying to add menu entry:', )
            print(e)

    def addMenuSubmenu(self, menu, label, icon, entries):
        try:
            cmds.menuItem(subMenu=True, tearOff=False, label=label, image=icon)
        except RuntimeError as e:
            print('Maya error while trying to create submenu:', )
            print(e)

        self.fillMenu(entries)

        try:
            cmds.setParent('..', menu=True)
        except RuntimeError as e:
            print('Maya error while trying to change menu parent:', )
            print(e)

    def addMenuCommand(self, menu, label, icon, command):
        try:
            cmds.menuItem(label=label, image=icon, command=command)
        except RuntimeError as e:
            print('Maya error while trying to change menu parent:', )
            print(e)
