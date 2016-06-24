import os
import pickle

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

import filetools


def load_model(filename):
    return pickle.load(open(filename))


if __name__ == '__main__':

    pickled_folder = os.path.join(HERE_PATH, 'pickled')

    regressor_folders = filetools.list_folders(pickled_folder)

    info_str = ''
    for folder in regressor_folders:
        files = filetools.list_files(folder, ['*.pkl'])

        dataset_name = os.path.split(folder)[1]
        info_str += '###\n{}\n###\n'.format(dataset_name)

        for f in files:

            basename = os.path.basename(f)
            (fname, ext) = os.path.splitext(basename)

            info_str += '\n## {}\n'.format(fname)

            clfs = load_model(f)

            for dim, clf in enumerate(clfs):
                info_str += '\n- Dim:{}'.format(dim)

                info_str += '\nScoring: {}'.format(clf.scoring)

                info_str += '\nBest Param: {}'.format(clf.best_params_)

                info_str += '\nBest Score Mean: {}'.format(clf.best_score_)

                best_id = -1
                for i, s in enumerate(clf.grid_scores_):
                    if s.mean_validation_score == clf.best_score_:
                        best_id = i
                        break

                best_std = clf.grid_scores_[best_id].cv_validation_scores.std()

                info_str += '\nBest Score Std: {}'.format(best_std)

                info_str += '\nParam Grid: {}'.format(clf.param_grid)

                info_str += '\n'

            info_str += '\n'

    # save to file
    save_file = os.path.join(HERE_PATH, 'regressors_info.txt')

    with open(save_file, "w") as f:
        f.write(info_str)
