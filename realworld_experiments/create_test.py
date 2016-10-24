import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

#
import json

import filetools

#
from utils.xp_utils import XPTools
from utils.filenaming import INFO_FILENAME

TEST_FOLDER = os.path.join(HERE_PATH, 'tests')

# order is really important here!! do not change
ENVIRONMENT_CONF = {
    'm_mins': [0, 0, 0, 0],
    'm_maxs': [1, 1, 1, 1],
    's_mins': [0, 0, 0],
    's_maxs': [1, 1, 1],
    'oils_list': ["dep", "octanol", "octanoic", "pentanol"],
    'features_list': ["lifetime", "speed", "wobble"]}


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def generate_xp(pool_folder, oil_ratios, n_xp_total):

    filetools.ensure_dir(pool_folder)


    # info for xp
    info = {}
    info['n_xp_total'] = n_xp_total
    info['environment_conf'] = ENVIRONMENT_CONF

    info_file = os.path.join(pool_folder, INFO_FILENAME)
    save_to_json(info, info_file)

    #
    xp_tools = XPTools(pool_folder)

    for i in range(n_xp_total):
        # if not saved yet, save it
        if not xp_tools.is_xp_created(i):
            xp_tools.save_XP_to_xp_number(oil_ratios, i)


if __name__ == '__main__':


    pool_folder = os.path.join(TEST_FOLDER, 'repeat_13_randomgoal_seed11_23deg_fan')

    oil_ratios = {
        "dep": 0.92019434642566544,
        "octanol": 0.7492601802279919,
        "octanoic": 0.0,
        "pentanol": 0.84013885086802531
    }

    n_xp_total = 8

    generate_xp(pool_folder, oil_ratios, n_xp_total)
