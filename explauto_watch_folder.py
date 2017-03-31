#!/usr/bin/python

import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

##
from explauto_tools.explauto_xp import ExplautoXP


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    xpgen = ExplautoXP(pool_folder, verbose=True)
    xpgen.monitor()
