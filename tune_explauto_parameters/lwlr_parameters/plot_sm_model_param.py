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


def plot_grid_info(grid_info, trait, space, bbox_to_anchor=(0.2, 1), legend_title=None, legend_color=[0.8, 0.8, 0.8]):

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
    if bbox_to_anchor is not None:
        legend = plt.legend(legend_names, bbox_to_anchor=bbox_to_anchor, fontsize=fontsize, title=legend_title, frameon=True, fancybox=True)
        frame = legend.get_frame()
        frame.set_facecolor(legend_color)

    return fig, ax


def save_and_close_fig(filebasename, exts=['.png', '.eps', '.svg'], dpi=100):
    for ext in exts:
        # save
        filepath = filebasename + ext
        plt.savefig(filepath, dpi=dpi)
    plt.close()



if __name__ == '__main__':

    plotfolder = os.path.join(HERE_PATH, 'plot')


    filename = os.path.join(HERE_PATH, 'cv_sm_model_param.json')
    grid_info = load_grid_results(filename)

    # cmaes_sigma
    fig = plot_grid_info(grid_info, 'cmaes_sigma', 'motor', bbox_to_anchor=(0.2, 1), legend_title='$\Sigma_{cmaes}$')

    plt.xlabel('Parameter Set Number', fontsize=fontsize)
    plt.ylabel('Inverse Prediction Error', fontsize=fontsize)
    plt.margins(0.2)
    plt.tight_layout()

    save_and_close_fig(os.path.join(plotfolder, 'cmaes_sigma'))

    # following this we select cmaes_sigma = 0.01
    selected_cmaes_sigma = 0.01
    selected_index = np.where(grid_info['cmaes_sigma'] == selected_cmaes_sigma)[0]
    selected_grid_info = {}
    for k, v in grid_info.items():
        if type(v) == list:
            selected_grid_info[k] = [v[i] for i in selected_index]
        else:
            selected_grid_info[k] = v[selected_index]

    # maxfevals
    fig = plt.figure(figsize=(12, 8))
    for i, space in enumerate(['motor', 'time']):
        legend_names = []
        ax = plt.subplot(1, 2, i + 1)

        options = np.unique(selected_grid_info['maxfevals'])
        for j, o in enumerate(options):
            idx = np.where(selected_grid_info['maxfevals'] == o)

            if space == 'motor':
                means = selected_grid_info['mean_motor'][idx]
            elif space == 'time':
                means = selected_grid_info['mean_time'][idx]
            elif space == 'sensori':
                means = selected_grid_info['mean_sensori'][idx]

            mean = np.mean(means)
            std = np.std(means)

            plt.errorbar(j, mean, yerr=std, fmt='o', capsize=10, elinewidth=3)
            legend_names.append(str(o))

            plt.xlabel('maxfevals', fontsize=fontsize)
            if space == 'motor':
                plt.ylabel('Inverse Prediction Error', fontsize=fontsize)
                plt.ylim([0.3, 0.4])
            elif space == 'time':
                plt.ylabel('Execution Time', fontsize=fontsize)
                plt.ylim([0, 0.1])


            ticks_str = [str(v) for v in options]
            plt.xticks(range(len(ticks_str)), ticks_str)
            plt.margins(0.2)
            plt.tight_layout()
            plt.xlim([-0.5, len(options) - 0.5])


    save_and_close_fig(os.path.join(plotfolder, 'maxfevals'))

    # following this we select maxfevals = 10
    grid_info = selected_grid_info
    selected_maxfevals = 20
    selected_index = np.where(grid_info['maxfevals'] == selected_maxfevals)[0]
    selected_grid_info = {}
    for k, v in grid_info.items():
        if type(v) == list:
            selected_grid_info[k] = [v[i] for i in selected_index]
        else:
            selected_grid_info[k] = v[selected_index]

    # lwlr k
    fig = plt.figure(figsize=(12, 8))
    for i, space in enumerate(['sensori', 'motor']):
        legend_names = []
        ax = plt.subplot(1, 2, i + 1)

        options = np.unique(selected_grid_info['k'])
        for o in options:
            idx = np.where(selected_grid_info['k'] == o)[0]

            if space == 'motor':
                means = selected_grid_info['mean_motor'][idx]
                stds = selected_grid_info['std_motor'][idx]
            elif space == 'sensori':
                means = selected_grid_info['mean_sensori'][idx]
                stds = selected_grid_info['std_sensori'][idx]

            plt.errorbar(idx, means, yerr=stds, fmt='o', capsize=10, elinewidth=3)
            legend_names.append(str(o))

            plt.xlabel('k', fontsize=fontsize)
            if space == 'motor':
                plt.ylabel('Inverse Prediction Error', fontsize=fontsize)
                plt.ylim([0.3, 0.4])
            elif space == 'sensori':
                plt.ylabel('Forward Prediction Error', fontsize=fontsize)
                plt.ylim([0.08, 0.18])

            ticks_str = [str(v) for v in selected_grid_info['k']]
            plt.xticks(range(len(ticks_str)), ticks_str)
            plt.margins(0.2)
            plt.tight_layout()
            plt.xlim([-0.5, len(selected_grid_info['k']) - 0.5])

    save_and_close_fig(os.path.join(plotfolder, 'k_lwlr'))
