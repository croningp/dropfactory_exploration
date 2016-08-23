#!/usr/bin/python
import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


import json

import numpy as np

from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

import filetools

from utils.xp_utils import xp_maker
from utils.xp_utils import XPTools

from utils.seed import set_seed

from utils.filenaming import XP_FEATURES_FILENAME
from utils.filenaming import REPEATS_FOLDERNAME
from utils.filenaming import REPEATS_INFO_FILENAME


N_XP_TO_REPEAT = 15
N_REPEATS_EACH = 8
FOLDERNAME_N_DIGIT = 2
FOLDERNAME_SPACE_CHAR = '_'


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


def select_n_prototypes(X, n_prototype):
    # normalize between 0 and 1 so all distance are equal in each dimension, this is important to cover as best as possible the space
    # also n_prototype should be << then the element in X to have a quite uniformaly distributed output, this is the case for us
    maxs = np.max(X, axis=0)
    mins = np.min(X, axis=0)
    X_selection = (X - mins) / maxs

    # prepare and fit the kmeans
    km = KMeans(n_prototype)
    km.fit(X_selection)

    # find point in original data that is the closest to the kmeans centers
    selected_X = []
    selected_index = []
    for center in km.cluster_centers_:
        Y = cdist(X_selection, [center], 'euclidean')
        index = np.argmin(Y)
        selected_index.append(index)
        selected_X.append(X[index, :])  # the one in X (input), corresponding index than in X_selection

    return np.array(selected_X), selected_index


def generate_repeat_xp_folder(root_path, i_xp, i_repeat):

    i_xp_str = filetools.generate_n_digit_name(i_xp, n_digit=FOLDERNAME_N_DIGIT)

    i_repeat_str = filetools.generate_n_digit_name(i_repeat, n_digit=FOLDERNAME_N_DIGIT)

    foldername = i_xp_str + FOLDERNAME_SPACE_CHAR + i_repeat_str

    return os.path.join(root_path, foldername)


def generate_repeats(path):

    if not os.path.exists(path):
        raise Exception('{} does not exists'.format(path))

    #
    xp_tool = XPTools(path)

    # setting the seed, to ensure repeatability
    set_seed(xp_tool.info_dict['seed'])

    # gather data, they are returned in order from 0 to n
    X = xp_tool.get_all_params()
    y = xp_tool.get_all_sensory()

    # select repeats well spread over the observed space
    _, selected_y_index = select_n_prototypes(y, N_XP_TO_REPEAT)

    print 'XP selected are: {}'.format(selected_y_index)

    #
    repeats_folder = os.path.join(path, REPEATS_FOLDERNAME)

    if os.path.exists(repeats_folder):
        raise Exception('{} already setup! Make the conscious act of deleting it just to avoid unexpected concequences :)'.format(repeats_folder))

    filetools.ensure_dir(repeats_folder)

    # save info
    repeats_info = {}
    repeats_info['n_xp'] = N_XP_TO_REPEAT
    repeats_info['n_repeats'] = N_REPEATS_EACH
    repeats_info['xp_number'] = selected_y_index

    repeats_info_file = os.path.join(repeats_folder, REPEATS_INFO_FILENAME)
    save_to_json(repeats_info, repeats_info_file)

    # generate experiments
    for i_xp, xp_number in enumerate(selected_y_index):
        for i_repeat in range(N_REPEATS_EACH):

            params = X[xp_number, :]

            oil_ratios = xp_tool.params_to_oils(params)

            xp_folder = generate_repeat_xp_folder(repeats_folder, i_xp, i_repeat)

            xp_maker.save_XP_to_folder(oil_ratios, xp_folder)

    print 'Repeat XP generated at {}'.format(repeats_folder)


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Need 1 arguments, the path of xp already done'

    path = os.path.join(HERE_PATH, sys.argv[1])

    generate_repeats(path)
