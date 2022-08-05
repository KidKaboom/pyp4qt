import os

from P4 import P4, P4Exception

import pyp4qt.utils
from pyp4qt.utils import logger

def connect(p4):
    if not p4.connected():
        # By setting P4's CWD to the settings folder, the user can create a 
        # P4CONFIG file per app. If they have already set an absolute path
        # for P4CONFIG, then this will have no effect.
        # Otherwise P4 will search upwards until it finds a p4config file
        from pyp4qt.apps import interop
        p4.cwd = interop.get_settings_path()

        logger().info('Connecting to server... %s' % p4.port)
        logger().debug('Using p4config file: %s' % p4.p4config_file)
        pyp4qt.utils.connect()

    try:
        root = p4.fetch_client()
    except P4Exception as e:
        logger().info('Attempting to login...')
        try:
            from pyp4qt.qt import LoginWindow
            LoginWindow.setP4Password(p4)
        except P4Exception as e:
            logger().warning('Couldn\'t login to server')
            p4.disconnect()
            raise

        try:
            root = p4.fetch_client()
        except P4Exception as e:
            raise e

        logger().info('Connected to server! [%s]' % (root))

    try:
        tmp = p4.run_info()
        info = tmp[0]
    except P4Exception as e:
        logger().error(e.msg)
        raise e

    if info['clientName'] == '*unknown*':
        msg = 'Perforce client is unknown, please edit your P4CONFIG file and specify a value for P4CLIENT or use "p4 set"'
        logger().debug(p4.cwd)
        logger().debug('P4CONFIG=%s' % os.environ.get('P4CONFIG'))
        logger().error(msg)
        raise ValueError(msg)

    # By default the cwd will be the same as the host's executable location,
    # so change it to the workspace root
    try:
        p4.cwd = info['client_root']
        logger().debug('Setting P4 cwd to %s', p4.cwd)
    except P4Exception as e:
        logger().error(e.msg)
        raise e    

    # for key in info:
    #     logger().debug( '\t%s:\t%s' % (key, info[key]) )

    logger().debug("Perforce CWD: %s" % p4.cwd)
