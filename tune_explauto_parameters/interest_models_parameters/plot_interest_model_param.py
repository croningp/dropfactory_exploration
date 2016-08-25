import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import json
import numpy as np

from scipy.spatial.distance import pdist

import filetools

import matplotlib
import matplotlib.pyplot as plt
import seaborn

# design figure
fontsize = 22
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)
matplotlib.rcParams.update({'font.size': fontsize})


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


def load_interest_tree_results(foldername):

    result_files = filetools.list_files(foldername)

    grid_results = {}
    tmp_result = read_from_json(result_files[0])
    for k in tmp_result.keys():
        grid_results[k] = []

    for f in result_files:
        results = read_from_json(f)
        for k, v in results.items():
            grid_results[k].append(v)

    return grid_results


def find_tree_config_subset(grid_results, tree_config_subset):

    idx = []

    for i, tree_config in enumerate(grid_results['tree_config']):
        valid = True
        for k, v in tree_config_subset.items():
            if k == 'sampling_mode':
                for k_samp, v_samp in tree_config_subset[k].items():
                    if v_samp != tree_config[k][k_samp]:
                        valid = False
            else:
                if v != tree_config[k]:
                    valid = False

        if valid:
            idx.append(i)

    return idx


def hist_from_all_Xy(all_Xy, bins = np.linspace(0, 1.5, 101)):

    hists = []
    for Xy in all_Xy:
        dist = pdist(Xy)
        hist, _ = np.histogram(dist, bins=bins)
        hists.append(hist / float(len(dist)))

    x_plot = np.diff(bins)/2 + bins[:-1]
    mean_dist = np.mean(hists, axis=0)
    std_dist = np.std(hists, axis=0)

    return x_plot, mean_dist, std_dist, bins


if __name__ == '__main__':

    result_folder = os.path.join(HERE_PATH, 'interest_tree_results')

    grid_results = load_interest_tree_results(result_folder)
    random_goal = read_from_json('random_goal.json')
    random_params = read_from_json('random_params.json')


    #
    # idx = find_tree_config_subset(grid_results, {'sampling_mode': {'volume': False}})
    # means = np.array(grid_results['mean_diversity_motor'])[idx]
    # stds = np.array(grid_results['std_diversity_motor'])[idx]
    # plt.errorbar(idx, means, yerr=stds, fmt='o', capsize=10, elinewidth=3)
    #
    #
    # idx = find_tree_config_subset(grid_results, {'sampling_mode': {'volume': True}})
    # means = np.array(grid_results['mean_diversity_motor'])[idx]
    # stds = np.array(grid_results['std_diversity_motor'])[idx]
    # plt.errorbar(idx, means, yerr=stds, fmt='o', capsize=10, elinewidth=3)




    plt.figure()

    for all_y in grid_results['all_y']:

        x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(all_y)
        plt.plot(x_plot, mean_dist, 'b')

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_goal['all_y'])
    plt.plot(x_plot, mean_dist, 'r')

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_params['all_y'])
    plt.plot(x_plot, mean_dist, 'g')

    plt.figure()

    for all_X in grid_results['all_X']:

        x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(all_X)
        plt.plot(x_plot, mean_dist, 'b')

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_goal['all_X'])
    plt.plot(x_plot, mean_dist, 'r')

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_params['all_X'])
    plt.plot(x_plot, mean_dist, 'g')
