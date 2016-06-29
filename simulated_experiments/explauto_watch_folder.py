import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

##
from explauto_tools.explauto_xp import ExplautoXP


if __name__ == '__main__':

    pool_folder = os.path.join(HERE_PATH, 'random_goal', '0')

    xpgen = ExplautoXP(pool_folder, verbose=True)
    xpgen.monitor()
