import os
import logging

logging.basicConfig(
    format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
    level=logging.DEBUG
)

LOGGER = logging.getLogger("Perforce")
GLOBALS_PATH = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(GLOBALS_PATH)
ICONS_DIR = os.path.join(SRC_DIR, "icons")
CONFIG_DIR = os.path.join(SRC_DIR, "config")
MENU_CONFIG_FILE = os.path.join(CONFIG_DIR, "menu_config.ini")
DCC = "standalone"
