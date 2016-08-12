import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

from utils.seed import set_seed


import tools


if __name__ == '__main__':

    set_seed(0)

    results = tools.run_random_motor()
    tools.save_to_json(results, os.path.join(HERE_PATH, 'random_motor.json'))
