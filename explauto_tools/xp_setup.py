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
import numpy as np

import filetools

#
from utils.seed import set_seed
from utils.xp_utils import XPTools
from utils.filenaming import INFO_FILENAME

N_XP_TOTAL = 1000
N_XP_BUFFER = 8

# order is really important here!! do not change
ENVIRONMENT_CONF = {
    'm_mins': [0, 0, 0, 0],
    'm_maxs': [1, 1, 1, 1],
    's_mins': [0, 0, 0],
    's_maxs': [1, 1, 1],
    'oils_list': ["dep", "octanol", "octanoic", "pentanol"],
    'features_list': ["lifetime", "speed", "wobble"]}

# determined by test in tune_explauto_parameters
MODEL_PARAMS = {'fwd': 'LWLR', 'k': 10, 'inv': 'CMAES', 'cmaes_sigma': 0.05, 'maxfevals': 20}


RANDOM_GOAL_INTEREST_MODEL_INFO = {'method': 'random_goal'}


TREE_CONFIG = {'max_points_per_region': 50,
               'max_depth': 20,
               'split_mode': 'best_interest_diff',
               'dist_min': 0.,
               'dist_max': 10.,
               'power': 1.,
               'progress_win_size': 25,
               'progress_measure': 'abs_deriv_smooth',
               'sampling_mode': {'mode': 'softmax',
                                 'param': 0.4,
                                 'multiscale': False,
                                 'volume': True}}

TREE_INTEREST_MODEL_INFO = {
    'method': 'interest_tree',
    'config': TREE_CONFIG}


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def generate_random_oil_ratios():
    ratios = np.random.rand(4)
    oil_names = ['octanol', 'octanoic', 'pentanol', 'dep']  # the order here does not matter, as long as the naming is correct
    oil_ratios = {}
    for i, oil_name in enumerate(oil_names):
        oil_ratios[oil_name] = ratios[i]
    return oil_ratios


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


def create_random_params_XP(pool_folder, seed, n_xp_total):
    filetools.ensure_dir(pool_folder)

    # info for xp
    info = {}
    info['seed'] = seed
    info['n_xp_total'] = N_XP_TOTAL
    info['environment_conf'] = ENVIRONMENT_CONF

    info_file = os.path.join(pool_folder, INFO_FILENAME)
    if os.path.exists(info_file):
        raise Exception('{} already setup! Make the conscious act of deleting it just to avoid unexpected concequences :)'.format(info_file))
    save_to_json(info, info_file)

    #
    xp_tools = XPTools(pool_folder)

    # set the seed
    set_seed(seed)

    for i in range(n_xp_total):
        # we need to generate them all to not loose track of the random generator state, wether or not it is already saved
        oil_ratios = generate_random_oil_ratios()
        # if not saved yet, save it
        if not xp_tools.is_xp_created(i):
            xp_tools.save_XP_to_xp_number(oil_ratios, i)


def create_random_params_xp(base_folder, seed):
    pool_folder = os.path.join(base_folder, 'random_params', str(seed))
    create_random_params_XP(pool_folder, seed, N_XP_TOTAL)


def create_random_goal_xp(base_folder, seed):
    pool_folder = os.path.join(base_folder, 'random_goal', str(seed))

    xp_config = build_xp_config(
        seed=seed,
        n_xp_total=N_XP_TOTAL,
        n_xp_buffer=N_XP_BUFFER,
        environment_conf=ENVIRONMENT_CONF,
        model_params=MODEL_PARAMS,
        interest_model_info=RANDOM_GOAL_INTEREST_MODEL_INFO)

    setup_experiment(pool_folder, xp_config)


def create_interest_tree_xp(base_folder, seed):
    pool_folder = os.path.join(base_folder, 'interest_tree', str(seed))

    xp_config = build_xp_config(
        seed=seed,
        n_xp_total=N_XP_TOTAL,
        n_xp_buffer=N_XP_BUFFER,
        environment_conf=ENVIRONMENT_CONF,
        model_params=MODEL_PARAMS,
        interest_model_info=TREE_INTEREST_MODEL_INFO)

    setup_experiment(pool_folder, xp_config)
