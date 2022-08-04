import unittest
import logging

from pyp4qt.AppInterop import interop
from pyp4qt.GUI import initMenu

from test_perforce import TestingEnvironment


class PerforceUITests(unittest.TestCase):
    def setUp(self):
        window, app = interop.setupEnvironment()
        logging.basicConfig(level=logging.DEBUG)

        self.p4 = TestingEnvironment()
        initMenu(self.p4)

        # window.show()
        # app.exec_()

    def testOne(self):
        self.failUnless(True)
