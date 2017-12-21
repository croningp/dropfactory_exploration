import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..', '..')
sys.path.append(root_path)

dropfactory_path = os.path.join(root_path, '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

##
import numpy as np

from tools.xp_maker import generate_next_XP_foldername
from tools.xp_maker import save_XP_dict_to_folder
from tools.xp_maker import make_basic_XP_dict

import filetools

#edit experimental parameter (time, recipe, repeats) here
EXPERIMENT_DURATION_IN_SEC = 5*60
N_REPEATS = 20
EXPERIMENT_FOLDER = os.path.join(HERE_PATH, 'experiments')

if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Need 1 arguments, the path of the folder to save experiments to'

    pool_folder = os.path.join(EXPERIMENT_FOLDER, sys.argv[1])
    if os.path.exists(pool_folder):
        raise Exception('{} already exists, delete it if you really want to'.format(pool_folder))


    #

    for _ in range(N_REPEATS):
        ## init XP_dict
        xp_folder = generate_next_XP_foldername(pool_folder)
        XP_dict = make_basic_XP_dict(xp_folder)


        oil_ratios = {
            "dep": 1,
            "octanol": 0,
            "octanoic": 0,
            "pentanol": 0
        }
        XP_dict['oil_formulation'] = oil_ratios

        ## update video duration
        XP_dict['video_info']['duration'] = EXPERIMENT_DURATION_IN_SEC

        ## save
        save_XP_dict_to_folder(XP_dict, xp_folder)
