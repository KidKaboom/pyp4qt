import unittest
import logging

from pyp4qt.apps import interop
from pyp4qt.utils import initMenu

from test_perforce import TestingEnvironment


class PerforceUITests(unittest.TestCase):
    def setUp(self):
        window, app = interop.setup_env()
        logging.basicConfig(level=logging.DEBUG)

        self.p4 = TestingEnvironment()
        initMenu(self.p4)

        # window.show()
        # app.exec_()

    def testOne(self):
        self.failUnless(True)
