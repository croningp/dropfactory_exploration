#!/usr/bin/python

import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

#
from explauto_tools import xp_setup


def create_xp(kind, im_name, seed):

    if kind == 'real':
        base_folder = os.path.join(HERE_PATH, 'realworld_experiments')
    elif kind == 'simu':
        base_folder = os.path.join(HERE_PATH, 'simulated_experiments')
    else:
        raise Exception('kind {} not handled'.format(kind))

    if im_name == 'random_params':
        xp_setup.create_random_params_xp(base_folder, seed)
    elif im_name == 'random_goal':
        xp_setup.create_random_goal_xp(base_folder, seed)
    elif im_name == 'interest_tree':
        xp_setup.create_interest_tree_xp(base_folder, seed)
    else:
        raise Exception('im_name {} not handled'.format(im_name))

if __name__ == '__main__':

    import sys

    if len(sys.argv) != 4:
        print 'Need 3 arguments'

    create_xp(sys.argv[1], sys.argv[2], int(sys.argv[3]))
