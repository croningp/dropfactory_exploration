import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

##
import time
import json
import numpy as np

from explauto import Agent
from explauto.experiment import Experiment
from explauto import InterestModel

from explauto.sensorimotor_model.non_parametric import NonParametric
from explauto.interest_model.tree import InterestTree, competence_exp

from scipy.spatial.distance import pdist

from models.regression.tools import load_model
clf = load_model(os.path.join(root_path, 'models/regression/pickled/octanoic/KernelRidge-RBF.pkl'))

from explauto_tools.droplet_environment import DropletEnvironment

conf = dict(m_mins=[0, 0, 0, 0],
            m_maxs=[1, 1, 1, 1],
            s_mins=[0, 0, 0],
            s_maxs=[1, 1, 1],
            out_dims = [0, 1, 2],
            clf=clf)

environment = DropletEnvironment(**conf)


N_ITERATION = 1000  # as per our protocol
N_REPEAT = 10

# as selected in ../lwlr_parameters
params = {'fwd': 'LWLR', 'k': 20, 'inv': 'CMAES', 'cmaes_sigma': 0.01, 'maxfevals': 5}


def run_xp(environment, sm_model, im_model, n_iter):

    agent = Agent(environment.conf, sm_model, im_model)
    xp = Experiment(environment, agent)
    xp.run(n_iter)
    return xp


def mean_dist_between_observations(X):
    dists = pdist(X)
    return np.mean(dists, axis=0), np.std(dists, axis=0)


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def run_im_model(im_model, n_iter):
    sm_model = NonParametric(environment.conf, **params)

    xp = run_xp(environment, sm_model, im_model, n_iter)

    X = xp.log.logs['motor']
    y = xp.log.logs['sensori']

    div_motor = mean_dist_between_observations(X)
    div_sensori = mean_dist_between_observations(y)

    del(sm_model)
    del(xp)

    return X, y, div_motor, div_sensori


def run_random_motor(n_iter=N_ITERATION, n_xp=N_REPEAT):

    all_X = []
    all_y = []
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):
        start_time = time.time()
        print '{}/{}'.format(i, n_xp)

        im_model = InterestModel.from_configuration(environment.conf, environment.conf.m_dims, 'random')

        X, y, div_motor, div_sensori = run_im_model(im_model, n_iter)
        del(im_model)

        all_X.append(X.tolist())
        all_y.append(y.tolist())
        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

        print 'Took {} seconds'.format(time.time() - start_time)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)
    results['all_X'] = all_X
    results['all_y'] = all_y

    return results


def run_random_goal(n_iter=N_ITERATION, n_xp=N_REPEAT):

    all_X = []
    all_y = []
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):
        start_time = time.time()
        print '{}/{}'.format(i, n_xp)

        im_model = InterestModel.from_configuration(environment.conf, environment.conf.s_dims, 'random')

        X, y, div_motor, div_sensori = run_im_model(im_model, n_iter)
        del(im_model)

        all_X.append(X.tolist())
        all_y.append(y.tolist())
        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

        print 'Took {} seconds'.format(time.time() - start_time)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)
    results['all_X'] = all_X
    results['all_y'] = all_y

    return results


def run_interest_tree(tree_config, n_iter=N_ITERATION, n_xp=N_REPEAT):

    all_X = []
    all_y = []
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):
        start_time = time.time()
        print '{}/{}'.format(i, n_xp)

        im_model = InterestTree(environment.conf, environment.conf.s_dims, **tree_config)

        X, y, div_motor, div_sensori = run_im_model(im_model, n_iter)
        del(im_model)

        all_X.append(X.tolist())
        all_y.append(y.tolist())
        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

        print 'Took {} seconds'.format(time.time() - start_time)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)
    results['all_X'] = all_X
    results['all_y'] = all_y

    return results
