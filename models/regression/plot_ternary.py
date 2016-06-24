import os
import time
import pickle
import numpy as np
import itertools

import matplotlib.pyplot as plt
import ternary


# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

import filetools

from datasets.tools import load_dataset


def load_model(filename):
    return pickle.load(open(filename))


def plot_and_save_all_ternaries(clfs, regressor_name, compound_names, fitness_names, regressor_plot_foldername, scale=100, fontsize=20):

    for i, fitness_name in enumerate(fitness_names):

        nCompound = len(compound_names)
        combinations = itertools.combinations(range(nCompound), nCompound - 1)

        for combination in combinations:

            fig, tax = plot_ternary(clfs[i], nCompound, combination, scale)

            coumpound_string, right_axis_label, left_axis_label, bottom_axis_label = forge_coumpound_string_and_axis_label(combination)

            # set title
            title = fitness_name + ' ' + regressor_name + ' (' + coumpound_string + ')'
            tax.set_title(title, fontsize=fontsize)

            # Set Axis labels and Title
            tax.left_axis_label(left_axis_label, fontsize=fontsize)
            tax.right_axis_label(right_axis_label, fontsize=fontsize)
            tax.bottom_axis_label(bottom_axis_label, fontsize=fontsize)

            ticks = list(np.linspace(0, 1, 11))
            loc = list(np.linspace(0, scale, 11))
            tax.ticks(ticks=ticks, locations=loc, axis='lbr', linewidth=1, multiple=5)

            # Remove default Matplotlib Axes
            tax.clear_matplotlib_ticks()
            fig.patch.set_visible(False)

            plt.show(block=False)
            time.sleep(0.1)

            # save
            save_folder = os.path.join(regressor_plot_foldername, fitness_name)
            filetools.ensure_dir(save_folder)
            filename = coumpound_string + ".png"
            filepath = os.path.join(save_folder, filename)

            fig.set_size_inches(12, 8)
            plt.savefig(filepath, dpi=100)
            time.sleep(0.1)
            plt.close()


def forge_coumpound_string_and_axis_label(combination):
    i = 0
    coumpound_string = ''
    for coumpound_idx in combination:
        coumpound_string += compound_names[coumpound_idx]
        coumpound_string += '_'

        # this is the name on the exis of the ternarty plot
        if i == 0:
            right_axis_label = compound_names[coumpound_idx]
        elif i == 1:
            left_axis_label = compound_names[coumpound_idx]
        elif i == 2:
            bottom_axis_label = compound_names[coumpound_idx]
        i += 1

    coumpound_string = coumpound_string[:-1]

    return coumpound_string, right_axis_label, left_axis_label, bottom_axis_label


def plot_ternary(clf, nCompound, combination, scale=50):

    # function called by ternary to estimate the value at each point
    def compute_value(s):
        x_ternary = np.zeros((nCompound,))
        for i, coumpound_idx in enumerate(combination):
            x_ternary[coumpound_idx] = s[i]

        value = clf.predict(x_ternary)
        return value.item()

    fig, tax = ternary.figure(scale=scale)
    tax.heatmapf(compute_value, boundary=True, style="triangular")

    return fig, tax


if __name__ == '__main__':

    save_folder = os.path.join(HERE_PATH, 'plot')
    pickled_folder = os.path.join(HERE_PATH, 'pickled')
    dataset_folder = os.path.join(HERE_PATH, '..', '..', 'datasets')

    datasets = filetools.list_folders(dataset_folder)

    for dataset in datasets:

        dataset_name = os.path.split(dataset)[1]
        plot_foldername = os.path.join(save_folder, dataset_name)
        pickled_foldername = os.path.join(pickled_folder, dataset_name)

        (_, _, dataset_info, _) = load_dataset(dataset_name)

        compound_names = dataset_info['x_keys']
        fitness_names = dataset_info['y_keys']

        model_files = filetools.list_files(pickled_foldername, ['*.pkl'])

        for model_file in model_files:
            clfs = load_model(model_file)

            basename = os.path.basename(model_file)
            (regressor_name, _) = os.path.splitext(basename)

            regressor_plot_foldername = os.path.join(plot_foldername, regressor_name)

            plot_and_save_all_ternaries(clfs, regressor_name, compound_names, fitness_names, regressor_plot_foldername)
