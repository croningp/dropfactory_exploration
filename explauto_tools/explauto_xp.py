import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

# global
import time
import json
import numpy as np

# global, no standard
from explauto.utils import rand_bounds
from explauto.utils.config import make_configuration
from explauto.sensorimotor_model.non_parametric import NonParametric
from explauto.interest_model.random import RandomInterest
from explauto.interest_model.tree import InterestTree
from explauto.interest_model.tree import competence_exp
from explauto.exceptions import ExplautoBootstrapError

# local
from utils.seed import set_seed
from explauto_tools.xp_utils import XPTools


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


class ExplautoXP(object):

    def __init__(self, pool_folder, sleep_time=1, verbose=False):
        self.xp_tools = XPTools(pool_folder)
        self.sleep_time = sleep_time
        self.verbose = verbose

        info_dict = self.xp_tools.info_dict
        self.seed = info_dict['seed']
        self.n_xp_total = info_dict['n_xp_total']
        self.n_xp_buffer = info_dict['n_xp_buffer']

        self.i_create_xp = 0
        self.i_wait_for_result = 0
        self.delta_i = 0

        self.is_initialized = False

    def init_explauto_side(self):
        info_dict = self.xp_tools.info_dict
        self.parse_environment_conf(info_dict['environment_conf'])
        self.parse_sensorimotor_model(info_dict['model_params'])
        self.parse_interest_model(info_dict['interest_model_info'])

    def parse_environment_conf(self, environment_conf):
        conf_dict = {}
        conf_keys = ['m_mins', 'm_maxs', 's_mins', 's_maxs']
        for k in conf_keys:
            conf_dict[k] = environment_conf[k]
        self.conf = make_configuration(**conf_dict)

    def parse_sensorimotor_model(self, model_params):
        self.sensorimotor_model = NonParametric(self.conf, **model_params)

    def parse_interest_model(self, interest_model_info):
        self.method = interest_model_info['method']

        if self.method == 'random_goal':
            self.interest_model = RandomInterest(self.conf, self.conf.s_dims)

        elif self.method == 'interest_tree':
            tree_config = interest_model_info['config']

            dist_min = float(tree_config['dist_min'])
            del(tree_config['dist_min'])

            dist_max = float(tree_config['dist_max'])
            del(tree_config['dist_max'])

            power = float(tree_config['power'])
            del(tree_config['power'])

            tree_config['competence_measure'] = lambda target, reached: competence_exp(target, reached, dist_min, dist_max, power)

            self.interest_model = InterestTree(self.conf, self.conf.s_dims, **tree_config)

        self.expl_dims = self.interest_model.expl_dims
        self.inf_dims = sorted(list(set(self.conf.dims) - set(self.expl_dims)))

    def infer(self, expl_dims, inf_dims, x):
        try:
            y = self.sensorimotor_model.infer(expl_dims,
                                              inf_dims,
                                              x.flatten())
        except ExplautoBootstrapError:
            if self.verbose:
                print 'Sensorimotor model not bootstrapped yet, infering at random'
            y = rand_bounds(self.conf.bounds[:, inf_dims]).flatten()
        return y

    def get_next_experiments(self):
        target_features = self.interest_model.sample()

        params = self.infer(self.expl_dims, self.inf_dims, target_features)
        oil_ratios = self.xp_tools.params_to_oils(params)

        explauto_info = {}
        explauto_info['targeted_features'] = target_features.tolist()

        return oil_ratios, explauto_info

    def update_with_xp_number(self, xp_number):
        """
        update sm_model with info from a particular xp_folder
        xp_folder must contain a params.json file and a features.json file
        """
        # extract params / motor command
        m_performed = self.xp_tools.get_params_from_xp_number(xp_number)
        # extract goal
        s_goal = self.xp_tools.get_goal_from_xp_number(xp_number)
        # extract features / sensory info
        s_reached = self.xp_tools.get_sensory_from_xp_number(xp_number)

        # update sensory and interest
        self.sensorimotor_model.update(m_performed, s_reached)
        self.interest_model.update(np.hstack((m_performed, s_goal)), np.hstack((m_performed, s_reached)))

    def check_same_experiment(self, xp_number, oil_ratios, explauto_info):

        stored_XP_dict = self.xp_tools.get_XP_dict_from_xp_number(xp_number)
        to_check_XP_dict = self.xp_tools.make_XP_dict(oil_ratios, xp_number)
        if stored_XP_dict != to_check_XP_dict:
            raise Exception('Something wrong when comparing XP_dict, possible seed problem!')

        stored_goal = self.xp_tools.get_goal_from_xp_number(xp_number)
        to_check_goal = explauto_info['targeted_features']
        if stored_goal != to_check_goal:
            raise Exception('Something wrong when comparing goals, possible seed problem!')

    def create_XP_at_xp_number(self, xp_number):
        # get parameters for xp
        oil_ratios, explauto_info = self.get_next_experiments()
        # if already exist, check the generated data are the same, just another check that random seed actually works
        if self.xp_tools.is_xp_created(xp_number):
            self.check_same_experiment(xp_number, oil_ratios, explauto_info)
        else:  # if does not exist create xp
            self.xp_tools.save_XP_to_xp_number(oil_ratios, xp_number)
            self.xp_tools.save_explauto_info_to_xp_number(explauto_info, xp_number)

    def init(self):
        self.init_explauto_side()
        set_seed(self.seed, verbose=self.verbose)

        self.is_initialized = True

    def reset(self):
        self.i_create_xp = 0
        self.i_wait_for_result = 0
        self.delta_i = 0

        self.is_initialized = False

    def increment_xp_number(self):
        self.i_create_xp += 1
        self.delta_i = self.i_create_xp - self.i_wait_for_result
        if self.delta_i == self.n_xp_buffer:
            self.i_wait_for_result += 1

    def build_up_to(self, xp_number):
        if xp_number > self.n_xp_total:
            raise Exception('Asked to build till {}, further ahead than total_xp of {}'.format(xp_number, self.n_xp_total))

        if not self.xp_tools.is_xp_performed(xp_number):
            raise Exception('xp number {} not performed, cannot build model up to it'.format(xp_number))

        if xp_number < self.i_wait_for_result - 1:
            self.reset()

        while xp_number >= self.i_wait_for_result + 1:
            self.step(verbose=False)

    def monitor(self):
        self.reset()
        while self.n_xp_total >= self.i_wait_for_result + 1:
            self.step(verbose=True)
        print '###\nCongratulation, all XP from {} have finished!!'.format(self.xp_tools.pool_folder)

    def step(self, verbose=True):
        if verbose:
            print '###'

        # init is not done yet
        if not self.is_initialized:
            if verbose:
                print 'Reinitializing models..'
            self.init()

        # if xp number within max total create new xp
        if self.i_create_xp < self.n_xp_total:
            if verbose:
                print 'Creating XP number: {}'.format(self.i_create_xp)
            self.create_XP_at_xp_number(self.i_create_xp)
        else:
            if verbose:
                print 'Total XP reached, no more XP to generate'

        # check results
        if self.i_wait_for_result <= self.n_xp_total:
            if self.delta_i > self.n_xp_buffer:
                raise Exception('Something wrong in xp generator, more xp ahead than buffer allows, should never be raised')
            elif self.delta_i == self.n_xp_buffer:
                # wait till result of xp ready
                if verbose:
                    print 'Waiting for results from XP number {}'.format(self.i_wait_for_result)
                while not self.xp_tools.is_xp_performed(self.i_wait_for_result):
                    time.sleep(self.sleep_time)  # wait till file is created
                # update sm_model and im_model
                self.update_with_xp_number(self.i_wait_for_result)
            else:
                if verbose:
                    print 'Not enough buffer XP to wait for results'
        else:
            if verbose:
                print 'Reached n_xp_total of {}, nothing to be performed'.format(self.n_xp_total)

        self.increment_xp_number()
