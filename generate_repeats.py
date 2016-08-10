#!/usr/bin/python

import os
import json

import numpy as np

from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

import filetools


FEATURES_FILENAME = 'features.json'


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


def get_all_xp_info_from_poolfolder(poolfolder):

    xp_folders = filetools.list_folders(poolfolder)

    X = []
    y = []
    for folder in xp_folders:
        feature_file = os.path.join(folder, FEATURES_FILENAME)
        if os.path.exists(feature_file):

            X.append()
            y.append()


def generate_repeats(path):

    if not os.path.exists(path):
        raise Exception('{} does not exists'.format(path))


    features = {}
    features['lifetime'] = droplet_features['ratio_frame_active']
    features['speed'] = droplet_features['average_speed']
    features['wobble'] = droplet_features['average_circularity_variation']



if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Need 1 arguments, the path of xp already done'

    generate_repeats(sys.argv[1])
