import re

from P4 import P4, P4Exception
from pyp4qt.utils import logger
from pyp4qt.perforce_utils import SetupConnection
from pyp4qt.qt.ErrorMessageWindow import displayErrorUI

def queryChangelists( p4, status = None):
    if not status:
        args = ["changes"]
    else:
        args = ["changes", "-s", status]

    try:
        return p4.run(args)
    except P4Exception as e:
        logger().warning(e)
        raise e

def submitChange(p4, files, description, callback, keepCheckedOut = False):
    # Shitty method #1
    logger().info("Files Passed for submission = {0}".format(files))
    
    print "Opened ", p4.run_opened("...")

    fullChangelist = p4.run_opened("-u", p4.user, "-C", p4.client, "...")
    
    if not fullChangelist:
        raise P4Exception("File changelist is empty")

    fileList = []
    opened = [ p4.run_opened("-u", p4.user, "-C", p4.client, file)[0] for file in files ]
   
    changeFiles = [ entry['clientFile'] for entry in opened ]# change._files

    logger().info("Changelist = {0}".format(changeFiles))

    for changeFile in changeFiles:
        if changeFile in files:
            fileList.append(changeFile)
        else:
            logger().warning("File {0} ({1}) not in changelist".format(changeFile, p4.run_opened(changeFile)[0]['action']))
            
    logger().info("Final changelist files = {0}".format(fileList))

    logger().debug([x['clientFile'] for x in fullChangelist])
    logger().debug([x['clientFile'] for x in opened])

    notSubmitted = list(set( [ x['clientFile'] for x in fullChangelist ] ) - set( [ x['clientFile'] for x in opened ] ))

    if notSubmitted:
        p4.run_revert("-k", notSubmitted)

    try:
        p4.progress = callback 
        p4.handler = callback

        if keepCheckedOut:
            result = p4.run_submit("-r", "-d", description, progress=callback, handler=callback)
        else:
            result = p4.run_submit("-d", description, progress=callback, handler=callback)
        logger().info(result)
    except P4Exception as e:
        logger().warning(e)
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
    #     logger().info(result)
    # except P4Exception as e:
    #     logger().warning(e)
    #     raise e

def syncPreviousRevision(p4, file, revision, description):
    logger().info(p4.run_sync("-f", "{0}#{1}".format(file, revision)))

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
            logger().info(p4.run_revert("-k", file))
        except P4Exception as e:
            errors.append(e)
        
        try:
            logger().info(p4.run_edit("-c", changeId, file))
        except P4Exception as e:
            errors.append(e)
            
        try:
            logger().info(p4.run_sync("-f", file))
        except P4Exception as e:
            errors.append(e)
        
        try:
            logger().info(p4.run_resolve("-ay"))
        except P4Exception as e:
            errors.append(e)

        try:
            change = p4.fetch_change(changeId)
        except P4Exception as e:
            errors.append(e)
            
        try:
            logger().info(p4.run_submit(change))
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
                logger().info("Deleting change {0} on client {1}".format(list['change'], list['client']))
                try:
                    p4.run_unlock("-c", list['change'])
                    p4.run_revert("-c", list['change'], "...")
                except P4Exception as e:
                    pass
                logger().info(p4.run_change("-d", list['change']))
            if not isUser:
                logger().warning("User {0} doesn't own change {1}, can't delete".format(p4.user, list['change']))
            if not isClient:
                logger().warning("Client {0} doesn't own change {1}, can't delete".format(p4.client, list['change']))
        except P4Exception as e:
            logger().critical(e)