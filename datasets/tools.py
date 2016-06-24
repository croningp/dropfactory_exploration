import os
import json

import numpy as np

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def load_dataset(dataset_name):
    dataset_folder = os.path.join(HERE_PATH, dataset_name)
    x = np.loadtxt(os.path.join(dataset_folder, 'x.csv'))
    y = np.loadtxt(os.path.join(dataset_folder, 'y.csv'))
    with open(os.path.join(dataset_folder, 'info.json')) as f:
        info = json.load(f)
    with open(os.path.join(dataset_folder, 'path.json')) as f:
        path = json.load(f)
    return x, y, info, path
