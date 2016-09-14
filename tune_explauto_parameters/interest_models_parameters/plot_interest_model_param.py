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

    idx_in = []
    idx_out = []

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
            idx_in.append(i)
        else:
            idx_out.append(i)

    return idx_in, idx_out


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


def save_and_close_fig(filebasename, exts=['.png', '.eps', '.svg'], dpi=100):
    for ext in exts:
        # save
        filepath = filebasename + ext
        plt.savefig(filepath, dpi=dpi)
    plt.close()


if __name__ == '__main__':

    result_folder = os.path.join(HERE_PATH, 'interest_tree_results')

    grid_results = load_interest_tree_results(result_folder)
    random_goal = read_from_json('random_goal.json')
    random_params = read_from_json('random_params.json')

    #
    all_means = []
    all_means_dim0 = []
    for all_y in grid_results['all_y']:
        x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(all_y)
        all_means.append(mean_dist)
    all_means = np.array(all_means)

    # plot them all
    plot_folder = os.path.join(HERE_PATH, 'plot')

    all_hist_plot_folder = os.path.join(plot_folder, 'hists')
    filetools.ensure_dir(all_hist_plot_folder)

    for i, means in enumerate(all_means):
        for mean_dist in all_means:
            plt.plot(x_plot, mean_dist, 'b')

        x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_goal['all_y'])
        plt.plot(x_plot, mean_dist, 'y')

        x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_params['all_y'])
        plt.plot(x_plot, mean_dist, 'g')

        plt.plot(x_plot, means, 'r')

        for idx in [13, 24, 37]:
            plt.plot([x_plot[idx], x_plot[idx]], [0, 0.1], 'k--')

        plt.xlim([0, 1])
        plt.ylim([0, 0.1])
        plt.xlabel('Distance between observations', fontsize=fontsize)
        plt.ylabel('Ratio of experiments', fontsize=fontsize)
        plt.margins(0.2)
        plt.tight_layout()

        filebasename = os.path.join(all_hist_plot_folder, filetools.generate_n_digit_name(i))
        save_and_close_fig(filebasename, exts=['.png'])

    #
    # x_plot[13] -> 0.20250000000000001
    # x_plot[24] -> 0.36749999999999999
    # x_plot[37] -> 0.5625

    d13 = np.abs(all_means[:, 13] - np.min(all_means[:, 13]))
    d24 = np.abs(all_means[:, 24] - np.max(all_means[:, 24]))
    d37 = np.abs(all_means[:, 37] - np.max(all_means[:, 37]))

    # we minimize the sum of distances
    fitness = d13+d24+d37
    best_idx = np.argmin(fitness)

    print 'Best tree config is number {}'.format(best_idx)
    print grid_results['tree_config'][best_idx]

    #
    plt.figure(figsize=(12,10))

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_params['all_y'])
    plt.plot(x_plot, mean_dist, 'b')

    x_plot, mean_dist, std_dist, bins = hist_from_all_Xy(random_goal['all_y'])
    plt.plot(x_plot, mean_dist, 'g')

    plt.plot(x_plot, means, 'r')

    plt.xlim([0, 1])
    plt.ylim([0, 0.1])
    plt.xlabel('Distance between observations', fontsize=fontsize)
    plt.ylabel('Ratio of experiments', fontsize=fontsize)
    plt.legend(['random_goal', 'random params', 'best tree config'], fontsize=fontsize)
    plt.margins(0.2)
    plt.tight_layout()

    filebasename = os.path.join(plot_folder, 'best_tree')
    save_and_close_fig(filebasename, exts=['.png'])
