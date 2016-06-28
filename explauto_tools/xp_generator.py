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


class XPGenerator(object):

    def __init__(self, pool_folder):
        self.xp_tools = XPTools(pool_folder)
        self.parse_info()

    def parse_info(self):
        info_dict = self.xp_tools.info_dict
        self.seed = info_dict['seed']
        self.n_xp_total = info_dict['n_xp_total']
        self.n_xp_buffer = info_dict['n_xp_buffer']

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

    def run(self):
        # always set the seed first
        set_seed(self.seed)

        # we need to restart from zero all the time to not loose track of the random generator state, wether or not it is already saved
        i_create_xp = 0
        i_wait_for_result = 0
        all_xp_done = False
        while not all_xp_done:

            print '###'

            # if xp number within max total create new xp
            if i_create_xp <= self.n_xp_total:
                print 'Creating XP number: {}'.format(i_create_xp)
                create_xp_folder = self.xp_tools.generate_XP_foldername(i_create_xp)
                # get parameters for xp
                oil_ratios, explauto_info = self.get_next_experiments()
                # if already exist, check the generated data are the same, just another check that random seed actually works
                if os.path.exists(create_xp_folder):
                    print 'Check data equally generated to implement!!'
                else:  # if does not exist create xp
                    self.xp_tools.save_XP_to_folder(oil_ratios, create_xp_folder)
                    self.xp_tools.save_explauto_info(explauto_info, create_xp_folder)
            else:
                print 'Total XP reached, no more XP to generate'

            # check results
            delta_i = i_create_xp - i_wait_for_result
            if delta_i > self.n_xp_buffer:
                raise Exception('Something wrong in xp generator, more xp ahead than buffer allows, should never be raised')
            elif delta_i == self.n_xp_buffer:
                # wait till result of xp ready
                print 'Waiting for results from XP number {}'.format(i_wait_for_result)
                while not self.xp_tools.is_xp_performed(i_wait_for_result):
                    time.sleep(1)  # wait till file is created
                # update sm_model and im_model
                self.update_with_xp_number(i_wait_for_result)
            else:
                print 'Not enough buffer XP to wait for results'

            # increment xp_number
            i_create_xp += 1
            if delta_i == self.n_xp_buffer:
                i_wait_for_result += 1

            # exit conditions
            if i_create_xp > self.n_xp_total and i_wait_for_result > self.n_xp_total:
                all_xp_done = True

        print 'Congratulation all experiments in {} have been processed!!'.format(self.xp_tools.pool_folder)
