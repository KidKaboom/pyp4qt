import platform
import traceback
import os
import re

from P4 import P4, P4Exception

import pyp4qt.utils
from pyp4qt import utils
from pyp4qt.apps import interop
from pyp4qt.test_output_progress import TestOutputProgress
from pyp4qt.qt.SubmitProgressWindow import SubmitProgressUI

from pyp4qt.qt.LoginWindow import firstTimeLogin
from pyp4qt.qt.ErrorMessageWindow import displayErrorUI
from pyp4qt.qt import OpenedFilesWindow
from pyp4qt.qt import SubmitChangeWindow
from pyp4qt.qt import FileRevisionWindow

from PySide2 import QtCore, QtGui, QtWidgets

class MainShelf:

    def __init__(self, p4):
        self.p4 = p4
        self.deleteUI = None
        self.submitUI = None

    def close(self):
        # @ToDo this stll seems to be maya specific
        try:
            self.revisionUi.deleteLater()
        except Exception as e:
            print("Error cleaning up P4 revision UI : ", e)

        try:
            self.openedUi.deleteLater()
        except Exception as e:
            print("Error cleaning up P4 opened UI : ", e)

        # try:
        #     # Deleting maya menus is bad, but this is a dumb way of error checking
        #     if "PerforceMenu" in self.perforceMenu:
        #         interop.close_window(self.perforceMenu)
        #     else:
        #         raise RuntimeError("Menu name doesn't seem to belong to Perforce, not deleting")
        # except Exception  as e:
        #     print "Error cleaning up P4 menu : ", e

        try:
            self.submitUI.deleteLater()
        except Exception as e:
            print("Error cleaning up P4 submit UI : ", e)

        utils.logger().info("Disconnecting from server")
        try:
            self.p4.disconnect()
        except Exception as e:
            print("Error disconnecting P4 daemon : ", e)

    def validateConnected(self, function, *args):
        with self.p4.at_exception_level(P4.RAISE_ERRORS):
            try:
                result = self.p4.run_login('-s')
            except P4Exception as e:
                utils.logger().info('Connected to server, but no login session. Disconnecting and attempting to login again.')
                with self.p4.at_exception_level(P4.RAISE_NONE):
                    self.p4.disconnect()
            

        if not self.p4.connected():
            # QtWidgets.QMessageBox.critical(None, 'Perforce Error', "Not connected to Perforce server, please connect first.", QtWidgets.QMessageBox.Warning)
            self.connectToServer(args)
        else:
            # A little heavy handed, but forces the cwd to the client root even if we have a valid login ticket
            self.p4.cwd = self.p4.run_info()[0]['client_root'].replace('\\', '/')

        if not self.p4.connected():
            QtWidgets.QMessageBox.critical(None, 'Perforce Error', "Can't connect to server, check 'p4 set' for more information about what could be wrong", QtWidgets.QMessageBox.Warning)
        else:
            function(args)


    def addMenu(self):
        try:
            interop.close_window(self.perforceMenu)
        except:
            pass

        # @ToDo Hard coded icons are bad?

        menuEntries = [
            {'label': "Client Commands",            'divider': True},
            {'label': "Checkout File(s)",           'image': os.path.join(interop.get_icons_path(), "File0078.png"), 'command': lambda *args: self.validateConnected(self.checkoutFile, args)},
            {'label': "Checkout Folder",            'image': os.path.join(interop.get_icons_path(), "File0186.png"), 'command': lambda *args: self.validateConnected(self.checkoutFolder, args)},
            {'label': "Mark for Delete",            'image': os.path.join(interop.get_icons_path(), "File0253.png"), 'command': lambda *args: self.validateConnected(self.deleteFile, args)},
            {'label': "Show Changelist",            'image': os.path.join(interop.get_icons_path(), "File0252.png"), 'command': lambda *args: self.validateConnected(self.queryOpened, args)},
            {'label': "Depot Commands",             'divider': True},
            {'label': "Submit Change",              'image': os.path.join(interop.get_icons_path(), "File0107.png"), 'command': lambda *args: self.validateConnected(self.submitChange, args)},
            {'label': "Sync All",                   'image': os.path.join(interop.get_icons_path(), "File0175.png"), 'command': lambda *args: self.validateConnected(self.syncAllChanged, args)},
            {'label': "Sync All - Force",           'image': os.path.join(interop.get_icons_path(), "File0175.png"), 'command': lambda *args: self.validateConnected(self.syncAll, args)},
            # {'label': "Sync All References",        'image': os.path.join(interop.get_icons_path(), "File0320.png"), 'command': lambda *args: self.validateConnected(self.syncAllChanged, args)},
            #{'label': "Get Latest Scene",          'image': os.path.join(interop.get_icons_path(), "File0275.png"), command = self.syncFile},
            {'label': "Show Depot History",         'image': os.path.join(interop.get_icons_path(), "File0279.png"), 'command': lambda *args: self.validateConnected(self.fileRevisions, args)},

            {'label': "Scene",                      'divider': True},
            {'label': "File Status",                'image': os.path.join(interop.get_icons_path(), "File0409.png"), 'command': lambda *args: self.validateConnected(self.querySceneStatus, args)},

            {'label': "Utility",                    'divider': True},
            {'label': "Create Asset",               'image': os.path.join(interop.get_icons_path(), "File0352.png"), 'command': lambda *args: self.createAsset(args)},
            {'label': "Create Shot",                'image': os.path.join(interop.get_icons_path(), "File0104.png"), 'command': lambda *args: self.createShot(args)},
            # Submenu
            {
                'label': "Miscellaneous",           'image': os.path.join(interop.get_icons_path(), "File0411.png"), 'entries': [
                    {'label': "Server",                     'divider': True},
                    {'label': "Login as user",              'image': os.path.join(interop.get_icons_path(), "File0077.png"), 'command': lambda *args: self.validateConnected(self.loginAsUser, args)},
                    {'label': "Server Info",                'image': os.path.join(interop.get_icons_path(), "File0031.png"), 'command': lambda *args: self.validateConnected(self.queryServerStatus, args)},
                    {'label': "Workspace",                  'divider': True},
                    {'label': "Create Workspace",           'image': os.path.join(interop.get_icons_path(), "File0238.png"), 'command': lambda *args: self.validateConnected(self.createWorkspace, args)},
                    {'label': "Set Current Workspace",      'image': os.path.join(interop.get_icons_path(), "File0044.png"), 'command': lambda *args: self.validateConnected(self.setCurrentWorkspace, args)},
                    {'label': "Debug",                      'divider': True},
                    {'label': "Delete all pending changes", 'image': os.path.join(interop.get_icons_path(), "File0280.png"), 'command': lambda *args: self.validateConnected(self.deletePending, args)}
                ]
            },
            # {'label': "Connect to server",          'image': os.path.join(interop.get_icons_path(), "File0077.png"),    'command': self.connectToServer},
        ]

        self.menu = interop.create_menu(menuEntries)

    def removeMenu(self):
        interop.removeMenu(self.menu)

    def createShot(self, *args):
        shotNameDialog = QtWidgets.QInputDialog
        shotName = shotNameDialog.getText(
            interop.main_parent_window(), "Create Shot", "Shot Name:")

        if not shotName[1]:
            return

        if not shotName[0]:
            utils.logger().warning("Empty shot name")
            return

        shotNumDialog = QtWidgets.QInputDialog
        shotNum = shotNumDialog.getText(
            interop.main_parent_window(), "Create Shot", "Shot Number:")

        if not shotNum[1]:
            return

        if not shotNum[0]:
            utils.logger().warning("Empty shot number")
            return

        shotNumberInt = -1
        try:
            shotNumberInt = int(shotNum[0])
        except ValueError as e:
            utils.logger().warning(e)
            return

        utils.logger().info("Creating folder structure for shot {0}/{1} in {2}".format(
            shotName[0], shotNumberInt, self.p4.cwd))
        dir = utils.create_shot_folders(self.p4.cwd, shotName[0], shotNumberInt)
        self.run_checkoutFolder(None, dir)

    def createAsset(self, *args):
        assetNameDialog = QtWidgets.QInputDialog
        assetName = assetNameDialog.getText(
            interop.main_parent_window(), "Create Asset", "Asset Name:")

        if not assetName[1]:
            return

        if not assetName[0]:
            utils.logger().warning("Empty asset name")
            return

        utils.logger().info("Creating folder structure for asset {0} in {1}".format(
            assetName[0], self.p4.cwd))
        dir = utils.create_asset_folders(self.p4.cwd, assetName[0])
        self.run_checkoutFolder(None, dir)

    def connectToServer(self, *args):
        pyp4qt.utils.connect(self.p4)

    def loginAsUser(self, *args):
        LoginWindow.firstTimeLogin(enterUsername=True, enterPassword=True)

    def setCurrentWorkspace(self, *args):
        workspacePath = QtWidgets.QFileDialog.getExistingDirectory(
            interop.main_parent_window(), "Select existing workspace")

        for client in self.p4.run_clients():
            if workspacePath.replace("\\", "/") == client['Root'].replace("\\", "/"):
                root, client = os.path.split(str(workspacePath))
                self.p4.client = client

                utils.logger().info(
                    "Setting current client to {0}".format(client))
                # REALLY make sure we save the P4CLIENT variable
                if platform.system() == "Linux" or platform.system() == "Darwin":
                    os.environ['P4CLIENT'] = self.p4.client
                    utils.saveEnvironmentVariable("P4CLIENT", self.p4.client)
                else:
                    self.p4.set_env('P4CLIENT', self.p4.client)

                utils.writeToP4Config(
                    self.p4.p4config_file, "P4CLIENT", self.p4.client)
                break
        else:
            QtWidgets.QMessageBox.warning(
                interop.main_parent_window(), "Perforce Error", "{0} is not a workspace root".format(workspacePath))

    def createWorkspace(self, *args):
        workspaceRoot = None

        # @ToDo remove this, it's badly written right now. 
        # Safer to use P4V for the initial setup to rewrite this to be more reliable

        # Give the artist 3 chances to choose a folder (assuming they choose a bad path)
        tries = 3
        i = 0
        while i < tries:
            workspaceRoot = QtWidgets.QFileDialog.getExistingDirectory(
                interop.main_parent_window(), "Specify workspace root folder")
            i += 1
            if workspaceRoot:
                break
        else:
            raise IOError("Can't set workspace")

        try:
            workspaceSuffixDialog = QtWidgets.QInputDialog
            workspaceSuffix = workspaceSuffixDialog.getText(
                interop.main_parent_window(), "Workspace", "Optional Name Suffix (e.g. Uni, Home):")

            utils.createWorkspace(self.p4, workspaceRoot,
                                  str(workspaceSuffix[0]))
            utils.writeToP4Config(self.p4.p4config_file,
                                  "P4CLIENT", self.p4.client)
        except P4Exception as e:
            displayErrorUI(e)

    # Open up a sandboxed QFileDialog and run a command on all the selected
    # files (and log the output)
    def __processClientFile(self, title, finishCallback, preCallback, p4command, *p4args):
        fileDialog = QtWidgets.QFileDialog(interop.main_parent_window(), title, str(self.p4.cwd))

        def onEnter(*args):
            if not utils.is_path_in_client_root(self.p4, args[0]):
                fileDialog.setDirectory(self.p4.cwd)

        def onComplete(*args):
            selectedFiles = []
            error = None

            if preCallback:
                preCallback(fileDialog.selectedFiles())

            # Only add files if we didn't cancel
            if args[0] == 1:
                for file in fileDialog.selectedFiles():
                    if utils.is_path_in_client_root(self.p4, file):
                        try:
                            utils.logger().info(p4command(p4args, file))
                            selectedFiles.append(file)
                        except P4Exception as e:
                            utils.logger().warning(e)
                            error = e
                    else:
                        utils.logger().warning("{0} is not in client root.".format(file))

            fileDialog.deleteLater()
            if finishCallback:
                finishCallback(selectedFiles, error)

        fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        pyp4qt.utils.connect(onEnter)
        pyp4qt.utils.connect(onComplete)
        fileDialog.show()

    # Open up a QFileDialog sandboxed to only allow files relative to the workspace
    # and run a command on all the selected folders (and log the output)
    # %TODO This should be refactored to use the same code as __processClientFile
    def __processClientDirectory(self, title, finishCallback, preCallback, p4command, *p4args):
        fileDialog = QtWidgets.QFileDialog(interop.main_parent_window(), title, str(self.p4.cwd))

        def onEnter(*args):
            if not utils.is_path_in_client_root(self.p4, args[0]):
                fileDialog.setDirectory(self.p4.cwd)

        def onComplete(*args):
            selectedFiles = []
            error = None

            if preCallback:
                preCallback(fileDialog.selectedFiles())

            # Only add files if we didn't cancel
            if args[0] == 1:
                for file in fileDialog.selectedFiles():
                    if utils.is_path_in_client_root(self.p4, file):
                        try:
                            utils.logger().info(p4command(p4args, file))
                            selectedFiles.append(file)
                        except P4Exception as e:
                            utils.logger().warning(e)
                            error = e
                    else:
                        utils.logger().warning("{0} is not in client root.".format(file))

            fileDialog.deleteLater()
            if finishCallback:
                finishCallback(selectedFiles, error)

        fileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        pyp4qt.utils.connect(onEnter)
        pyp4qt.utils.connect(onComplete)
        fileDialog.show()

    def checkoutFile(self, *args):
        def openFirstFile(selected, error):
            if not error:
                if len(selected) == 1 and utils.query_extension(selected[0], interop.get_scene_files()):
                    if not interop.get_current_scene_file() == selected[0]:
                        result = QtWidgets.QMessageBox.question(
                                    interop.main_parent_window(),
                                    "Open Scene?",
                                    "Do you want to open the checked out scene?",
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

                        if result == QtWidgets.QMessageBox.StandardButton.Yes:
                            interop.open_scene(selected[0])

        self.__processClientFile("Checkout file(s)", openFirstFile, None, self.run_checkoutFile)

    def checkoutFolder(self, *args):
        self.__processClientDirectory("Checkout file(s)", None, None, self.run_checkoutFolder)

    def run_checkoutFolder(self, *args):
        allFiles = []
        for folder in args[1:]:
            allFiles += utils.query_dir(folder)

        self.run_checkoutFile(None, *allFiles)

    def deletePending(self, *args):
        changes = utils.query_changelists(self.p4, "pending")
        utils.force_changelist_delete(self.p4, changes)

    def run_checkoutFile(self, *args):
        for file in args[1:]:
            utils.logger().info("Processing {0}...".format(file))
            result = None
            try:
                # @ToDO set this up to use p4.at_exception_level
                result = self.p4.run_fstat(file)
            except P4Exception as e:
                pass

            try:
                if result:
                    if 'otherLock' in result[0]:
                        raise P4Exception("[Warning]: {0} already locked by {1}\"".format(file, result[0]['otherLock'][0]))
                    else:
                        utils.logger().info(self.p4.run_edit(file))
                        utils.logger().info(self.p4.run_lock(file))
                else:
                    utils.logger().info(self.p4.run_add(file))
                    utils.logger().info(self.p4.run_lock(file))
            except P4Exception as e:
                displayErrorUI(e)

    def deleteFile(self, *args):
        self.__processClientFile(
            "Delete file(s)", None, lambda x: utils.add_read_only_bit(x), self.p4.run_delete)

    def revertFile(self, *args):
        self.__processClientFile(
            "Revert file(s)", None, None, self.p4.run_revert, "-k")

    def lockFile(self, *args):
        self.__processClientFile("Lock file(s)", None, None, self.p4.run_lock)

    def unlockFile(self, *args):
        self.__processClientFile(
            "Unlock file(s)", None, None, self.p4.run_unlock)

    def lockThisFile(self, *args):
        raise NotImplementedError(
            "Scene lock not implemented (use regular lock)")

    def unlockThisFile(self, *args):
        raise NotImplementedError(
            "Scene unlock not implemented (use regular unlock)")

    def querySceneStatus(self, *args):
        try:
            scene = interop.get_current_scene_file()
            if not scene:
                utils.logger().warning("Current scene file isn't saved.")
                return

            with self.p4.at_exception_level(P4.RAISE_ERRORS):
                result = self.p4.run_fstat("-Oa", scene)[0]
            text = ''.join( ["{0} : {1}\n".format(x, result[x]) for x in result] )

            QtWidgets.QMessageBox.information(interop.main_parent_window(), "Scene Info", text)
        except P4Exception as e:
            displayErrorUI(e)

    def queryServerStatus(self, *args):
        try:
            result = self.p4.run_info()[0]
            text = ''.join( ["{0} : {1}\n".format(x, result[x]) for x in result] )

            QtWidgets.QMessageBox.information(interop.main_parent_window(), "Server Info", text)
        except P4Exception as e:
            displayErrorUI(e)

    def fileRevisions(self, *args):
        try:
            self.revisionUi.deleteLater()
        except:
            pass

        self.revisionUi = FileRevisionWindow.FileRevisionUI(self.p4)

        # Delete the UI if errors occur to avoid causing winEvent and event
        # errors (in Maya 2014)
        try:
            self.revisionUi.create()
            self.revisionUi.show()
        except:
            self.revisionUi.deleteLater()
            utils.logger().error(traceback.format_exc())

    def queryOpened(self, *args):
        try:
            self.openedUi.deleteLater()
        except:
            pass

        self.openedUi = OpenedFilesWindow.OpenedFilesUI()

        # Delete the UI if errors occur to avoid causing winEvent and event
        # errors (in Maya 2014)
        try:
            self.openedUi.create(self.p4)
            self.openedUi.show()
        except:
            self.openedUi.deleteLater()
            utils.logger().error(traceback.format_exc())

    def submitChange(self, *args):
        try:
            self.submitUI.deleteLater()
        except:
            pass

        self.submitUI = SubmitChangeWindow.SubmitChangeUi()

        # Delete the UI if errors occur to avoid causing winEvent
        # and event errors (in Maya 2014)
        try:
            files = self.p4.run_opened(
                "-u", self.p4.user, "-C", self.p4.client, "...")

            interop.refresh()

            entries = []
            for file in files:
                filePath = file['clientFile']

                entry = {'File': filePath,
                         'Folder': os.path.split(filePath)[0],
                         'Type': file['type'],
                         'Pending_Action': file['action'],
                         }

                entries.append(entry)

            print("Submit Files : ", files)

            self.submitUI.create(self.p4, entries)
            self.submitUI.show()
        except:
            self.submitUI.deleteLater()
            utils.logger().error(traceback.format_exc())

    def syncFile(self, *args):
        try:
            self.p4.run_sync("-f", interop.get_current_scene_file())
            utils.logger().info("Got latest revision for {0}".format(
                interop.get_current_scene_file()))
        except P4Exception as e:
            displayErrorUI(e)

    def syncAll(self, *args):
        reply = QtWidgets.QMessageBox.warning(interop.main_parent_window(), 
            'Are you sure?',
            'Are you sure? This will force every file to redownload and can take some time to complete.',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.No:
            return

        # progress = SubmitProgressUI(len(files))
        # progress.create("Submit Progress")

        # callback = TestOutputProgress(progress)

        # progress.show()

        try:
            self.p4.run_sync("-f", "...")
            utils.logger().info("Got latest revisions for client")
        except P4Exception as e:
            displayErrorUI(e)

    def syncAllChanged(self, *args):
        try:
            self.p4.run_sync("...")
            utils.logger().info("Got latest revisions for client")
        except P4Exception as e:
            displayErrorUI(e)