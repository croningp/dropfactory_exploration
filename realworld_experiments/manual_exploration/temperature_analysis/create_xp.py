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

from tools.xp_maker import add_XP_to_pool_folder

import filetools

N_REPEATS = 10
RECIPES_CSV_FILENAME = os.path.join(HERE_PATH, 'recipes_for_temperature_analysis.csv')
EXPERIMENT_FOLDER = os.path.join(HERE_PATH, 'experiments')

def load_recipes():
    data = np.loadtxt(RECIPES_CSV_FILENAME, delimiter=',', skiprows=1)
    # order is dep,octanol,octanoic,pentanol
    return data


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Need 1 arguments, the path of the folder to save experiments to'

    pool_folder = os.path.join(EXPERIMENT_FOLDER, sys.argv[1])
    if os.path.exists(pool_folder):
        raise Exception('{} already exists, delete it if you really want to'.format(pool_folder))


    #
    recipes = load_recipes()

    for _ in range(N_REPEATS):
        for recipy in recipes:
            oil_ratios = {
                "dep": recipy[0],
                "octanol": recipy[1],
                "octanoic": recipy[2],
                "pentanol": recipy[3]
            }
            add_XP_to_pool_folder(oil_ratios, pool_folder)
