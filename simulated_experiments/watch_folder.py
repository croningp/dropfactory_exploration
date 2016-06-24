import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

import json

###
from models.regression.tools import load_model
model_file = os.path.join(root_path, 'models', 'regression', 'pickled', 'octanoic', 'KernelRidge-RBF.pkl')
clf = load_model(model_file)

from explauto_tools import droplet_environment

# ["division", "directionality", "movement"]
conf = dict(m_mins=[0, 0, 0, 0],
            m_maxs=[1, 1, 1, 1],
            s_mins=[0, 0],
            s_maxs=[18, 5],
            out_dims=[1, 2],
            clf=clf)

environment = droplet_environment.DropletEnvironment(**conf)

##

xp_params_filename = 'params.json'
xp_features_filename = 'features.json'


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


def extract_param_array_from_XP_dict(XP_dict):

    params = [None, None, None, None]
    # ["dep", "octanol", "octanoic", "pentanol"]
    params[0] = XP_dict['formulation']['dep']
    params[1] = XP_dict['formulation']['octanol']
    params[2] = XP_dict['formulation']['octanoic']
    params[3] = XP_dict['formulation']['pentanol']
    return params


def run_and_save_experiment(folder, param_file):
    print '###\nProcessing {}'.format(param_file)
    XP_dict = read_from_json(param_file)
    params = extract_param_array_from_XP_dict(XP_dict)
    features = environment.update(params)

    feature_file = os.path.join(folder, xp_features_filename)

    data = {}
    data['directionality'] = features[0]
    data['movement'] = features[1]

    print 'Saving results at {}'.format(feature_file)
    save_to_json(data, feature_file)

##
pool_folder = os.path.join(HERE_PATH, 'random_params', '0')

from utils import watcher

filewatcher = watcher.Watcher(pool_folder, xp_params_filename, xp_features_filename, run_and_save_experiment)
