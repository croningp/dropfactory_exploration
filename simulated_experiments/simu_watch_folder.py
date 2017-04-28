#!/usr/bin/python

import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

import json


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)

###
from models.regression.tools import load_model
model_file = os.path.join(root_path, 'models', 'regression', 'pickled', 'octanoic', 'KernelRidge-RBF.pkl')
clf = load_model(model_file)

from explauto_tools import droplet_environment

# ["division", "directionality", "movement"]
# ["lifetime", "speed", "wobble"]
conf = dict(m_mins=[0, 0, 0, 0],
            m_maxs=[1, 1, 1, 1],
            s_mins=[0, 0, 0],
            s_maxs=[1, 1, 1],
            out_dims=[0, 1, 2],
            clf=clf)

environment = droplet_environment.DropletEnvironment(**conf)

##
from utils.filenaming import XP_PARAMS_FILENAME
from utils.filenaming import XP_FEATURES_FILENAME


def extract_param_array_from_XP_dict(XP_dict):

    params = [None, None, None, None]
    # ["dep", "octanol", "octanoic", "pentanol"]
    # order is really important here!! do not change
    params[0] = XP_dict['oil_formulation']['dep']
    params[1] = XP_dict['oil_formulation']['octanol']
    params[2] = XP_dict['oil_formulation']['octanoic']
    params[3] = XP_dict['oil_formulation']['pentanol']
    return params


def run_and_save_experiment(folder, param_file):
    print '###\nProcessing {}'.format(param_file)
    XP_dict = read_from_json(param_file)
    params = extract_param_array_from_XP_dict(XP_dict)
    features = environment.update(params)

    feature_file = os.path.join(folder, XP_FEATURES_FILENAME)

    # ["division", "directionality", "movement"]
    # ["lifetime", "speed", "wobble"]
    # faking it so the naming corresponds with the real experiment
    # this all simulation is just for dev and debug before going on real robot
    data = {}
    data['lifetime'] = features[0]
    data['speed'] = features[1]
    data['wobble'] = features[2]

    print 'Saving results at {}'.format(feature_file)
    save_to_json(data, feature_file)

##
from utils import watcher

if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    filewatcher = watcher.Watcher(pool_folder, XP_PARAMS_FILENAME, XP_FEATURES_FILENAME, run_and_save_experiment)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        filewatcher.join()
