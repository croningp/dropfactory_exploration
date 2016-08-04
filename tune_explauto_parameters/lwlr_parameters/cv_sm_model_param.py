import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

from utils.seed import set_seed
set_seed(0)

##
import time
import json
import numpy as np

from sklearn.grid_search import ParameterGrid
from sklearn.cross_validation import train_test_split

from explauto.sensorimotor_model.non_parametric import NonParametric

from explauto.utils.config import make_configuration

CONF_PARAM = dict(m_mins=[0, 0, 0, 0],
            m_maxs=[1, 1, 1, 1],
            s_mins=[0, 0, 0],
            s_maxs=[24, 18, 5])

CONF = make_configuration(**CONF_PARAM)


def train(params, X_train, y_train):
    sm_model = NonParametric(CONF, **params)
    for i in range(X_train.shape[0]):
        m = X_train[i, :]
        s = y_train[i, :]
        sm_model.update(m, s)
    return sm_model


def test(sm_model, X_test, y_test):

    m_errors = []
    s_errors = []
    times = []

    for i in range(X_test.shape[0]):
        m_true = X_test[i, :]
        s_true = y_test[i, :]

        start_time = time.time()
        m_pred = sm_model.inverse_prediction(s_true)
        s_pred = sm_model.forward_prediction(m_true)
        times.append(time.time() - start_time)

        m_error = np.linalg.norm(m_true - m_pred)
        s_error = np.linalg.norm(s_true - s_pred)

        m_errors.append(m_error)
        s_errors.append(s_error)

    return np.mean(m_errors), np.std(m_errors), np.mean(s_errors), np.std(s_errors), np.mean(times), np.std(times)


def cv_eval(params, X, y, n_fold=10, verbose=True):

    if verbose:
        print 'CV on {}'.format(params)

    m_errors = []
    s_errors = []
    times = []

    for i in range(n_fold):
        if verbose:
            print '{}/{}'.format(i + 1, n_fold)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1.0/n_fold)


        sm_model = train(params, X_train, y_train)

        mean_m, std_m, mean_s, std_s, mean_time, std_time = test(sm_model, X_test, y_test)

        m_errors.append(mean_m)
        s_errors.append(std_s)
        times.append(mean_time)

    return np.mean(m_errors), np.std(m_errors), np.mean(s_errors), np.std(s_errors), np.mean(times), np.std(times)


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':

    from datasets.tools import load_dataset
    X, y, info, path = load_dataset('octanoic')

    param_grid = {
        'fwd': ['LWLR'],
        'k': [5, 10, 15, 20, 30, 40, 50],
        'inv': ['CMAES'],
        'cmaes_sigma': [0.001, 0.005, 0.01, 0.05, 0.1],
        'maxfevals': [1000]
    }


    param_product = list(ParameterGrid(param_grid))

    grid_results = []

    for i, params in enumerate(param_product):

        print '###'
        print '{}/{}'.format(i + 1, len(param_product))

        mean_m, std_m, mean_s, std_s, mean_time, std_time = cv_eval(params, X, y)

        results = {}
        results['params'] = params
        results['mean_motor'] = mean_m
        results['std_motor'] = std_m
        results['mean_sensori'] = mean_s
        results['std_sensori'] = std_s
        results['mean_time'] = mean_time
        results['std_time'] = std_time

        grid_results.append(results)

    # save
    filename = os.path.join(HERE_PATH, 'cv_sm_model_param.json')
    save_to_json(grid_results, filename)
