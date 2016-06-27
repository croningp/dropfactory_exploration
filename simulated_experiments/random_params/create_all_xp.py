import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
dropfactory_path = os.path.join(HERE_PATH, '..', '..', '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

import logging
logging.basicConfig(level=logging.INFO)

##
import json
import numpy as np

import filetools

from tools.xp_maker import generate_XP_foldername
from tools.xp_maker import save_XP_to_folder
from utils.seed import set_seed


def generate_random_oil_ratios():
    ratios = np.random.rand(4)
    oil_names = ['octanol', 'octanoic', 'pentanol', 'dep']
    oil_ratios = {}
    for i, oil_name in enumerate(oil_names):
        oil_ratios[oil_name] = ratios[i]
    return oil_ratios


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    # change the seed
    SEED = 0
    N_XP = 1000

    pool_folder = os.path.join(HERE_PATH, str(SEED))
    filetools.ensure_dir(pool_folder)

    # info for xp
    info = {}
    info['seed'] = SEED

    infofile = os.path.join(pool_folder, 'info.json')

    save_to_json(info, infofile)

    # set the seed
    set_seed(SEED)

    for i in range(N_XP):
        # we need to generate them all to not loose track of the random generator state, wether or not it is already saved
        oil_ratios = generate_random_oil_ratios()
        # if not saved yet, save it
        xp_folder = generate_XP_foldername(pool_folder, i)
        if not os.path.exists(xp_folder):
            save_XP_to_folder(oil_ratios, xp_folder)
