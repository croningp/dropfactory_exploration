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

##
import json
import numpy as np

import filetools

from tools.xp_maker import add_XP_to_pool_folder

def proba_normalize(x):
    x = np.array(x, dtype=float)
    if np.sum(x) == 0:
        x = np.ones(x.shape)
    return x / np.sum(x, dtype=float)


def generate_random_oil_ratios():
    ratios = proba_normalize(np.random.rand(4))
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

    pool_folder = os.path.join(HERE_PATH, str(SEED))
    if os.path.exists(pool_folder):
        raise Exception('Folder/Seed already exists/used!')

    filetools.ensure_dir(pool_folder)

    info = {}
    info['seed'] = SEED

    infofile = os.path.join(pool_folder, 'info.json')

    save_to_json(info, infofile)

    # set the seed
    np.random.seed(SEED)

    for _ in range(1000):
        oil_ratios = generate_random_oil_ratios()
        add_XP_to_pool_folder(oil_ratios, pool_folder)
