import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

import logging
logging.basicConfig(level=logging.INFO)

##
from explauto_tools.xp_setup import build_xp_config
from explauto_tools.xp_setup import setup_experiment


N_XP_TOTAL = 1000
N_XP_BUFFER = 10

ENVIRONMENT_CONF = {
    'm_mins': [0, 0, 0, 0],
    'm_maxs': [1, 1, 1, 1],
    's_mins': [0, 0],
    's_maxs': [18, 5],
    'oils_list': ['dep', 'octanol', 'octanoic', 'pentanol'],
    'features_list': ['directionality', 'movement']}

MODEL_PARAMS = {'fwd': 'LWLR', 'k': 10, 'inv': 'CMAES', 'cmaes_sigma': 0.05, 'maxfevals': 20}

RANDOM_GOAL_INTEREST_MODEL_INFO = {'method': 'random_goal'}


if __name__ == '__main__':

    SEED = 0

    xp_config = build_xp_config(
        seed=SEED,
        n_xp_total=N_XP_TOTAL,
        n_xp_buffer=N_XP_BUFFER,
        environment_conf=ENVIRONMENT_CONF,
        model_params=MODEL_PARAMS,
        interest_model_info=RANDOM_GOAL_INTEREST_MODEL_INFO)

    pool_folder = os.path.join(HERE_PATH, 'random_goal', str(SEED))

    setup_experiment(pool_folder, xp_config)
