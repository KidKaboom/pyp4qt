import os
import logging

LOGGER = logging.getLogger("Perforce")
GLOBALS_PATH = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(GLOBALS_PATH)
ICONS_DIR = os.path.join(SRC_DIR, "icons")
