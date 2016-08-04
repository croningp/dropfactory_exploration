import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

##
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
            s_maxs=[24, 18, 5],
            out_dims = [0, 1, 2],
            clf=clf)

environment = DropletEnvironment(**conf)


params = {'fwd': 'LWLR', 'k': 10, 'inv': 'CMAES', 'cmaes_sigma': 0.05, 'maxfevals': 20}


def run_xp(environment, sm_model, im_model, n_iter):

    agent = Agent(environment.conf, sm_model, im_model)
    xp = Experiment(environment, agent)
    xp.run(n_iter)
    return xp


def mean_dist_between_observations(X, scale=False):

    if scale:
        X[:, 0] = X[:, 0] / 24.
        X[:, 1] = X[:, 1] / 18.
        X[:, 2] = X[:, 2] / 5.

    dists = pdist(X)

    return np.mean(dists, axis=0), np.std(dists, axis=0)


def diversity_from_log(log):

    div_motor, _ = mean_dist_between_observations(log.logs['motor'], scale=False)
    div_sensori, _ = mean_dist_between_observations(log.logs['sensori'], scale=True)

    return div_motor, div_sensori


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def run_im_model(im_model, n_iter):
    sm_model = NonParametric(environment.conf, **params)

    xp = run_xp(environment, sm_model, im_model, n_iter)

    div_motor, div_sensori = diversity_from_log(xp.log)

    del(sm_model)
    del(im_model)
    del(xp)

    return div_motor, div_sensori


def run_random_motor(n_iter=1000, n_xp=10):
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):

        print '{}/{}'.format(i, n_xp)

        im_model = InterestModel.from_configuration(environment.conf, environment.conf.m_dims, 'random')

        div_motor, div_sensori = run_im_model(im_model, n_iter)

        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)

    return results


def run_random_goal(n_iter=1000, n_xp=10):
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):

        print '{}/{}'.format(i, n_xp)

        im_model = InterestModel.from_configuration(environment.conf, environment.conf.s_dims, 'random')

        div_motor, div_sensori = run_im_model(im_model, n_iter)

        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)

    return results


def run_interest_tree(tree_config, n_iter=1000, n_xp=10):
    div_motors = []
    div_sensoris = []
    for i in range(n_xp):

        print '{}/{}'.format(i, n_xp)

        im_model = InterestTree(environment.conf, environment.conf.s_dims, **tree_config)

        div_motor, div_sensori = run_im_model(im_model, n_iter)

        div_motors.append(div_motor)
        div_sensoris.append(div_sensori)

    results = {}
    results['mean_motor'] = np.mean(div_motors)
    results['std_motor'] = np.std(div_motors)
    results['mean_sensori'] = np.mean(div_sensoris)
    results['std_sensori'] = np.std(div_sensoris)

    return results
