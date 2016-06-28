import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

##
import json

import filetools


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

INFO_FILENAME = 'info.json'

N_XP_TOTAL = 1000
N_XP_BUFFER = 10

ENVIRONMENT_CONF = {
    'm_mins': [0, 0, 0, 0],
    'm_maxs': [1, 1, 1, 1],
    's_mins': [0, 0],
    's_maxs': [18, 5],
    'oils_list': ["dep", "octanol", "octanoic", "pentanol"],
    'features_list': ["directionality", "movement"]}

MODEL_PARAMS = {'fwd': 'LWLR', 'k': 10, 'inv': 'CMAES', 'cmaes_sigma': 0.05, 'maxfevals': 20}

RANDOM_GOAL_INTEREST_MODEL_INFO = {'method': 'random_goal'}

TREE_CONFIG = {'max_points_per_region': 50.,
               'max_depth': 20,
               'split_mode': 'best_interest_diff',
               'dist_min': 0.,
               'dist_max': 10.,
               'power': 1.,
               'progress_win_size': 25.,
               'progress_measure': 'abs_deriv_smooth',
               'sampling_mode': {'mode': 'softmax',
                                 'param': 0.4,
                                 'multiscale': False,
                                 'volume': True}}

TREE_INTEREST_MODEL_INFO = {
    'method': 'random_goal',
    'config': TREE_CONFIG}


def build_xp_config(seed, n_xp_total, n_xp_buffer, environment_conf, model_params, interest_model_info):
    xp_config_dict = {}
    xp_config_dict['seed'] = seed
    xp_config_dict['n_xp_total'] = n_xp_total
    xp_config_dict['n_xp_buffer'] = n_xp_buffer
    xp_config_dict['environment_conf'] = environment_conf
    xp_config_dict['model_params'] = model_params
    xp_config_dict['interest_model_info'] = interest_model_info
    return xp_config_dict


def setup_experiment(pool_folder, xp_config):
    filetools.ensure_dir(pool_folder)

    info_file = os.path.join(pool_folder, INFO_FILENAME)
    if os.path.exists(info_file):
        raise Exception('{} already setup! Make the conscious act of deleting it just to avoid unexpected concequences :)'.format(info_file))
    save_to_json(xp_config, info_file)
