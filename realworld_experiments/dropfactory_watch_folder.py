import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
dropfactory_path = os.path.join(HERE_PATH, '..', '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

import logging
logging.basicConfig(level=logging.INFO)

###
from manager import manager
from tools.xp_watcher import XPWatcher


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    watcher = XPWatcher(manager, pool_folder)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        watcher.join()
