import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
dropfactory_path = os.path.join(HERE_PATH, '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

import logging
logging.basicConfig(level=logging.INFO)

###
from manager import manager
from tools.xp_watcher import XPWatcher

pool_folder = os.path.join(HERE_PATH, 'realworld_experiments', 'random', '0')

watcher = XPWatcher(manager, pool_folder)
