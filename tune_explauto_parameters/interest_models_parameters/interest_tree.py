import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

##
import copy
import time
import numpy as np

from sklearn.grid_search import ParameterGrid
from explauto.interest_model.competences import competence_dist, competence_exp

from utils.seed import set_seed

import tools


if __name__ == '__main__':

    set_seed(0)

    measure_dist = lambda target, reached: competence_dist(target, reached, 0., np.inf)

    measure_exp= lambda target, reached: competence_exp(target, reached, 0., np.inf, 1.)

    param_grid = {
        'max_points_per_region': [30, 50],
        'max_depth': [20],
        'split_mode': ['median', 'best_interest_diff'],
        'competence_measure': ['dist', 'exp'],
        'progress_win_size': [10, 25],
        'progress_measure': ['abs_deriv_smooth']
    }
    param_list = list(ParameterGrid(param_grid))

    sampling_mode_grid = {
        'mode': ['softmax'],
        'param': [0.1, 0.2, 0.4],
        'multiscale': [True, False],
        'volume': [True, False]
    }
    param_sampling_mode = list(ParameterGrid(sampling_mode_grid))

    # param_grid = {
    #     'max_points_per_region': [30],
    #     'max_depth': [20],
    #     'split_mode': ['best_interest_diff'],
    #     'competence_measure': ['dist'],
    #     'progress_win_size': [10],
    #     'progress_measure': ['abs_deriv_smooth']
    # }
    # param_list = list(ParameterGrid(param_grid))
    #
    # sampling_mode_grid = {
    #     'mode': ['softmax'],
    #     'param': [0.1],
    #     'multiscale': [True],
    #     'volume': [True]
    # }
    # param_sampling_mode = list(ParameterGrid(sampling_mode_grid))

    ##
    param_product = []
    for p in param_list:
        for s in param_sampling_mode:
            config = copy.deepcopy(p)
            config['sampling_mode'] = s
            param_product.append(config)

    ##
    results = []
    for i, tree_config in enumerate(param_product):

        start_time = time.time()
        print '###'
        print 'Running {}/{}: {}'.format(i + 1, len(param_product), tree_config)

        measure_name = tree_config['competence_measure']

        run_config = copy.deepcopy(tree_config)
        if measure_name == 'dist':
            run_config['competence_measure'] = measure_dist
        elif measure_name == 'exp':
            run_config['competence_measure'] = measure_exp

        result = tools.run_interest_tree(run_config)
        result['tree_config'] = tree_config
        results.append(result)

        print 'Took {} seconds'.format(time.time() - start_time)

    tools.save_to_json(results, os.path.join(HERE_PATH, 'interest_tree.json'))
