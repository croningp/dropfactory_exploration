import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import json
import numpy as np

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


def load_grid_results(filename):
    grid_results = read_from_json(filename)

    grid_info = {}
    grid_info['index'] = range(len(grid_results))

    for k in ['mean_motor', 'std_motor', 'mean_sensori', 'std_sensori', 'mean_time', 'std_time']:
        grid_info[k] = np.array([results[k] for results in grid_results])

    for k in ['cmaes_sigma', 'k', 'maxfevals']:
        grid_info[k] = np.array([results['params'][k] for results in grid_results])

    return grid_info


def plot_grid_info(grid_info, trait, space, bbox_to_anchor=(0.2, 1)):

    fig = plt.figure(figsize=(12, 8))
    ax = plt.subplot(1, 1, 1)

    legend_names = []

    options = np.unique(grid_info[trait])
    for o in options:
        idx = np.where(grid_info[trait] == o)[0]

        if space == 'motor':
            means = grid_info['mean_motor'][idx]
            stds = grid_info['std_motor'][idx]
        elif space == 'sensori':
            means = grid_info['mean_sensori'][idx]
            stds = grid_info['std_sensori'][idx]
        elif space == 'time':
            means = grid_info['mean_time'][idx]
            stds = grid_info['std_time'][idx]

        plt.errorbar(idx, means, yerr=stds, fmt='o', capsize=10, elinewidth=3)
        legend_names.append(str(o))

    plt.xlim([-1, len(grid_info[trait])])
    plt.legend(legend_names, bbox_to_anchor=bbox_to_anchor, fontsize=fontsize)

    return fig, ax


if __name__ == '__main__':

    # filename = os.path.join(HERE_PATH, 'maxfevals_info.json')
    # grid_info = load_grid_results(filename)

    # fig = plot_grid_info(grid_info, 'maxfevals', 'time', bbox_to_anchor=(0.2, 1))


    filename = os.path.join(HERE_PATH, 'cv_sm_model_param.json')
    grid_info = load_grid_results(filename)

    fig = plot_grid_info(grid_info, 'k', 'time', bbox_to_anchor=(1.15, 1))

    fig = plot_grid_info(grid_info, 'k', 'sensori', bbox_to_anchor=(1.15, 1))

    fig = plot_grid_info(grid_info, 'k', 'motor', bbox_to_anchor=(1.15, 1))

    fig = plot_grid_info(grid_info, 'cmaes_sigma', 'motor', bbox_to_anchor=(1.15, 1))

    fig = plot_grid_info(grid_info, 'cmaes_sigma', 'time', bbox_to_anchor=(1.15, 1))


    # ##
    # options = np.unique(ks)
    #
    # plt.figure(figsize=(12, 8))
    # ax = plt.subplot(1, 1, 1)
    # for o in options:
    #     idx = np.where(ks == o)[0]
    #     means = means_motor[idx]
    #     stds = stds_motor[idx]
    #     plt.errorbar(idx, means, yerr=stds, fmt='o', linewidth=0, capsize=10, elinewidth=3, label=str(o))
    #
    # plt.legend()
    #
    # ##
    # options = np.unique(sigmas)
    #
    # plt.figure(figsize=(12, 8))
    # ax = plt.subplot(1, 1, 1)
    # for o in options:
    #     idx = np.where(sigmas == o)[0]
    #     means = means_sensori[idx]
    #     stds = stds_sensori[idx]
    #     plt.errorbar(idx, means, yerr=stds, fmt='o', linewidth=0, capsize=10, elinewidth=3, label=str(o))
    #
    # plt.legend()
    #
    #
    # ##
    # options = np.unique(sigmas)
    #
    # plt.figure(figsize=(12, 8))
    # ax = plt.subplot(1, 1, 1)
    # for o in options:
    #     idx = np.where(sigmas == o)[0]
    #     means = means_motor[idx]
    #     stds = stds_motor[idx]
    #     plt.errorbar(idx, means, yerr=stds, fmt='o', linewidth=0, capsize=10, elinewidth=3, label=str(o))
    #
    # plt.legend()
    #
    # ##
    # options = np.unique(maxfevals)
    #
    # plt.figure(figsize=(12, 8))
    # ax = plt.subplot(1, 1, 1)
    # for o in options:
    #     idx = np.where(maxfevals == o)[0]
    #     means = means_motor[idx]
    #     stds = stds_motor[idx]
    #     plt.errorbar(idx, means, yerr=stds, fmt='o', linewidth=0, capsize=10, elinewidth=3, label=str(o))
    #
    # plt.legend()


    # plt.figure(figsize=(12, 8))
    # (_, caps, _) = plt.errorbar(ids, means_motor, yerr=stds_motor, linewidth=5.0, capsize=10, elinewidth=3)
    #
    # plt.figure(figsize=(12, 8))
    # (_, caps, _) = plt.errorbar(ids, means_sensori, yerr=stds_sensori, linewidth=5.0, capsize=10, elinewidth=3)
