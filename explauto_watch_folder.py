#!/usr/bin/python

import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

##
from explauto_tools.explauto_xp import ExplautoXP


def get_pool_folder(kind, im_name, seed):

    if kind == 'real':
        base_folder = os.path.join(HERE_PATH, 'realworld_experiments')
    elif kind == 'simu':
        base_folder = os.path.join(HERE_PATH, 'simulated_experiments')
    else:
        raise Exception('kind {} not handled'.format(kind))

    if im_name == 'random_params':
        pool_folder = os.path.join(base_folder, 'random_params')
    elif im_name == 'random_goal':
        pool_folder = os.path.join(base_folder, 'random_goal')
    elif im_name == 'interest_tree':
        pool_folder = os.path.join(base_folder, 'interest_tree')
    else:
        raise Exception('im_name {} not handled'.format(im_name))

    return os.path.join(pool_folder, str(seed))


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    xpgen = ExplautoXP(pool_folder, verbose=True)
    xpgen.monitor()
