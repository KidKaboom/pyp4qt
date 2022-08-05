import os
import traceback
import ntpath
import subprocess
import string
import re
import platform
import sys
import logging
import stat
import fileinput
import traceback

from P4 import P4, P4Exception

from pyp4qt.qt.ErrorMessageWindow import displayErrorUI


def p4Logger():
    return logging.getLogger("Perforce")


def importClass(modulePath, className):
    mod = __import__(modulePath, fromlist=[className])
    return getattr(mod, className)


def queryFilesInDirectory(rootDir):
    allFiles = []
    for root, dirnames, filenames in os.walk(rootDir):
        currentDir = ""
        if dirnames:
            currentDir = dirnames[0]

        fullPath = os.path.join(root, currentDir)

        for file in filenames:
            allFiles.append(os.path.join(fullPath, file))

    return allFiles


def makeDirectory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def makeEmptyFile(path):
    try:
        open(path, 'a').close()
    except IOError as e:
        print(e)


def makeEmptyDirectory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    makeEmptyFile(os.path.join(path, ".place-holder"))
    return path


def createAssetFolders(root, assetName):
    # @ToDo Make this more generic (or remove completely)
    rootDir = os.path.join(root, "assets")
    assetsDir = os.path.join(rootDir, assetName)

    makeDirectory(rootDir)
    makeDirectory(assetsDir)
    makeEmptyDirectory(os.path.join(assetsDir, "lookDev"))
    makeEmptyDirectory(os.path.join(assetsDir, "modelling"))
    makeEmptyDirectory(os.path.join(assetsDir, "rigging"))
    makeEmptyDirectory(os.path.join(assetsDir, "texturing"))

    return assetsDir


def createShotFolders(root, shotName, shotNumInput):
    # @ToDo Make this more generic (or remove completely)
    rootDir = os.path.join(root, "shots")
    shotsDir = os.path.join(rootDir, shotName)
    shotNum = "{0}0".format(format(shotNumInput, '02'))
    shotNumberDir = os.path.join(shotsDir, "{0}_sh_{1}".format(shotName, shotNum))

    makeDirectory(rootDir)
    makeDirectory(shotsDir)
    shot = makeDirectory(shotNumberDir)

    # Cg
    cg = makeDirectory(os.path.join(shot, "cg"))

    houdini = makeDirectory(os.path.join(cg, "houdini"))
    makeEmptyDirectory(os.path.join(houdini, "scenes"))

    maya = makeDirectory(os.path.join(cg, "maya"))
    makeEmptyDirectory(os.path.join(maya, "icons"))
    makeEmptyDirectory(os.path.join(maya, "scenes"))

    makeEmptyDirectory(os.path.join(shot, "comp"))
    makeEmptyDirectory(os.path.join(shot, "dailies"))
    makeEmptyDirectory(os.path.join(shot, "delivery"))
    makeEmptyDirectory(os.path.join(shot, "plates"))

    return shotNumberDir


def removeReadOnlyBit(files):
    for file in files:
        fileAtt = os.stat(file)[0]
        if (not fileAtt & stat.S_IWRITE):
            # File is read-only, so make it writeable
            os.chmod(file, stat.S_IWRITE)
        else:
            # File is writeable, so make it read-only
            # os.chmod(myFile, stat.S_IREAD)
            pass


def addReadOnlyBit(files):
    for file in files:
        fileAtt = os.stat(file)[0]
        if (not fileAtt & stat.S_IWRITE):
            # File is read-only, so make it writeable
            # os.chmod(file, stat.S_IWRITE)
            pass
        else:
            # File is writeable, so make it read-only
            os.chmod(file, stat.S_IREAD)


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def queryFileExtension(filePath, extensions=[]):
    if not extensions:
        return False

    extensions = [ext.lower() for ext in extensions]

    fileExt = os.path.splitext(filePath)[1]
    fileExt = fileExt.lower()

    return fileExt in extensions


def sessionInfo(session):
    """ Returns a dictionary of information from the current P4 session.

    Args:
        session (P4)

    Returns:
        dict()
    """
    result = dict()

    if session.connected():
        info = session.run("info")

        if info:
            result = info[0]

    return result


def clientRoot(session):
    """ Returns the current client root directory.

    Args:
        session (P4)

    Returns:
        str
    """
    return sessionInfo(session).get("clientRoot", str())


def isPathInClientRoot(session, path):
    """ Returns True if the path is in the client root.

    Args:
        session (P4)
        path (str)

    Returns:
        bool
    """
    if session.connected():
        client_root = session.run("info")[0].get("clientRoot", "")
        # print(root, path)
        # print(os.path.commonpath([root, path]) == root)

        return os.path.commonpath([client_root, path]) == client_root

    p4Logger().warning("{0} not in client root".format(path))
    return False


def inDirectory(file, directory):
    """ Returns True if file is in directory.

    Args:
        file (str)
        directory (str)

    Returns:
        bool
    """
    # make both absolute
    directory = os.path.join(os.path.realpath(directory), '')
    file = os.path.realpath(file)

    # return true, if the common prefix of both is equal to directory
    # e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return (os.path.commonprefix([directory, file]) == directory) or (
            os.path.abspath(file) == os.path.abspath(directory))


def parsePerforceError(e):
    eMsg = str(e).replace("[P4#run]", "")
    idx = eMsg.find('\t')
    firstPart = " ".join(eMsg[0:idx].split())
    firstPart = firstPart[:-1]

    secondPart = eMsg[idx:]
    secondPart = secondPart.replace('\\n', '\n')
    secondPart = secondPart.replace('"', '')
    secondPart = " ".join(secondPart.split())
    secondPart = secondPart.replace(' ', '', 1)  # Annoying space at the start, remove it

    eMsg = "{0}\n\n{1}".format(firstPart, secondPart)

    type = "info"
    if "[Warning]" in str(e):
        eMsg = eMsg.replace("[Warning]:", "")
        type = "warning"
    elif "[Error]" in str(e):
        eMsg = eMsg.replace("[Error]:", "")
        type = "error"

    return eMsg, type


def connect(p4):
    if not p4.connected():
        # By setting P4's CWD to the settings folder, the user can create a
        # P4CONFIG file per app. If they have already set an absolute path
        # for P4CONFIG, then this will have no effect.
        # Otherwise P4 will search upwards until it finds a p4config file
        from pyp4qt.apps import interop
        p4.cwd = interop.getSettingsPath()

        p4Logger().info('Connecting to server... %s' % p4.port)
        p4Logger().debug('Using p4config file: %s' % p4.p4config_file)
        p4.connect()

    try:
        root = p4.fetch_client()
    except P4Exception as e:
        p4Logger().info('Attempting to login...')
        try:
            from pyp4qt.qt import LoginWindow
            LoginWindow.setP4Password(p4)
        except P4Exception as e:
            p4Logger().warning('Couldn\'t login to server')
            p4.disconnect()
            raise

        try:
            root = p4.fetch_client()
        except P4Exception as e:
            raise e

        p4Logger().info('Connected to server! [%s]' % (root))

    try:
        tmp = p4.run_info()
        info = tmp[0]
    except P4Exception as e:
        p4Logger().error(e.msg)
        raise e

    if info['clientName'] == '*unknown*':
        msg = 'Perforce client is unknown, please edit your P4CONFIG file and specify a value for P4CLIENT or use "p4 set"'
        p4Logger().debug(p4.cwd)
        p4Logger().debug('P4CONFIG=%s' % os.environ.get('P4CONFIG'))
        p4Logger().error(msg)
        raise ValueError(msg)

    # By default the cwd will be the same as the host's executable location,
    # so change it to the workspace root
    try:
        p4.cwd = info['clientRoot']
        p4Logger().debug('Setting P4 cwd to %s', p4.cwd)
    except P4Exception as e:
        p4Logger().error(e.msg)
        raise e

        # for key in info:
    #     p4Logger().debug( '\t%s:\t%s' % (key, info[key]) )

    p4Logger().debug("Perforce CWD: %s" % p4.cwd)


def queryChangelists(p4, status=None):
    if not status:
        args = ["changes"]
    else:
        args = ["changes", "-s", status]

    try:
        return p4.run(args)
    except P4Exception as e:
        p4Logger().warning(e)
        raise e


def submitChange(p4, files, description, callback, keepCheckedOut=False):
    # Shitty method #1
    p4Logger().info("Files Passed for submission = {0}".format(files))

    print("Opened ", p4.run_opened("..."))

    fullChangelist = p4.run_opened("-u", p4.user, "-C", p4.client, "...")

    if not fullChangelist:
        raise P4Exception("File changelist is empty")

    fileList = []
    opened = [p4.run_opened("-u", p4.user, "-C", p4.client, file)[0] for file in files]

    changeFiles = [entry['clientFile'] for entry in opened]  # change._files

    p4Logger().info("Changelist = {0}".format(changeFiles))

    for changeFile in changeFiles:
        if changeFile in files:
            fileList.append(changeFile)
        else:
            p4Logger().warning(
                "File {0} ({1}) not in changelist".format(changeFile, p4.run_opened(changeFile)[0]['action']))

    p4Logger().info("Final changelist files = {0}".format(fileList))

    p4Logger().debug([x['clientFile'] for x in fullChangelist])
    p4Logger().debug([x['clientFile'] for x in opened])

    notSubmitted = list(set([x['clientFile'] for x in fullChangelist]) - set([x['clientFile'] for x in opened]))

    if notSubmitted:
        p4.run_revert("-k", notSubmitted)

    try:
        p4.progress = callback
        p4.handler = callback

        if keepCheckedOut:
            result = p4.run_submit("-r", "-d", description, progress=callback, handler=callback)
        else:
            result = p4.run_submit("-d", description, progress=callback, handler=callback)
        p4Logger().info(result)
    except P4Exception as e:
        p4Logger().warning(e)
        raise e

    p4.progress = None
    p4.handler = None

    # change = p4.fetch_change()

    # change._description = description

    # change._files = changeFile

    # try:
    #     if keepCheckedOut:
    #         result = p4.run_submit(change, "-r")
    #     else:
    #         result = p4.run_submit(change)
    #     p4Logger().info(result)
    # except P4Exception as e:
    #     p4Logger().warning(e)
    #     raise e


def syncPreviousRevision(p4, file, revision, description):
    p4Logger().info(p4.run_sync("-f", "{0}#{1}".format(file, revision)))

    change = p4.fetch_change()
    change._description = description

    result = p4.save_change(change)
    r = re.compile("Change ([1-9][0-9]*) created.")
    m = r.match(result[0])
    changeId = "0"
    if m:
        changeId = m.group(1)

    # Terrible exception handling but I need all the info I can for this to be artist proof
    try:
        errors = []

        # Try to remove from changelist if we have it checked out
        try:
            p4Logger().info(p4.run_revert("-k", file))
        except P4Exception as e:
            errors.append(e)

        try:
            p4Logger().info(p4.run_edit("-c", changeId, file))
        except P4Exception as e:
            errors.append(e)

        try:
            p4Logger().info(p4.run_sync("-f", file))
        except P4Exception as e:
            errors.append(e)

        try:
            p4Logger().info(p4.run_resolve("-ay"))
        except P4Exception as e:
            errors.append(e)

        try:
            change = p4.fetch_change(changeId)
        except P4Exception as e:
            errors.append(e)

        try:
            p4Logger().info(p4.run_submit(change))
        except P4Exception as e:
            errors.append(e)

        if errors:
            raise tuple(errors)
    except P4Exception as e:
        displayErrorUI(e)
        return False
    return True


def forceChangelistDelete(p4, lists):
    for list in lists:
        try:
            isUser = (list['user'] == p4.user)
            isClient = (list['client'] == p4.client)

            if isUser and isClient:
                p4Logger().info("Deleting change {0} on client {1}".format(list['change'], list['client']))
                try:
                    p4.run_unlock("-c", list['change'])
                    p4.run_revert("-c", list['change'], "...")
                except P4Exception as e:
                    pass
                p4Logger().info(p4.run_change("-d", list['change']))
            if not isUser:
                p4Logger().warning("User {0} doesn't own change {1}, can't delete".format(p4.user, list['change']))
            if not isClient:
                p4Logger().warning("Client {0} doesn't own change {1}, can't delete".format(p4.client, list['change']))
        except P4Exception as e:
            p4Logger().critical(e)
