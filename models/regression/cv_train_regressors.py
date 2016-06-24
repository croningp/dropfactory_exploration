import os
import pickle
import multiprocessing

from sklearn.grid_search import GridSearchCV


# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..')
sys.path.append(root_path)

import filetools

from datasets.tools import load_dataset


def train_model(dataset_name, model_info, scoring='mean_squared_error', cv=10, n_jobs=multiprocessing.cpu_count()):

    (dataset_X, dataset_Y, dataset_info, dataset_path) = load_dataset(dataset_name)

    # we train one regressor per Y dimension, because most regression models do not handle multiple dimensions
    clfs = []
    for i in range(dataset_Y.shape[1]):

        if 'clf' in model_info:
            clf = model_info['clf']
        else:
            clf = GridSearchCV(model_info['estimator'], model_info['param_grid'], scoring=scoring, cv=cv, n_jobs=n_jobs)

        print 'Training dimension {}/{}: {}'.format(i + 1, dataset_Y.shape[1], dataset_info['y_keys'][i])
        clf.fit(dataset_X, dataset_Y[:, i])

        clfs.append(clf)

    return clfs


def save_model(clfs, filename):
    filetools.ensure_dir(os.path.dirname(filename))
    pickle.dump(clfs, open(filename, "wb"))


if __name__ == '__main__':

    save_folder = os.path.join(HERE_PATH, 'pickled')
    dataset_folder = os.path.join(HERE_PATH, '..', '..', 'datasets')

    datasets = filetools.list_folders(dataset_folder)

    for dataset in datasets:

        dataset_name = os.path.split(dataset)[1]
        pickled_foldername = os.path.join(save_folder, dataset_name)
        filetools.ensure_dir(pickled_foldername)

        from sklearn.tree import DecisionTreeRegressor
        model_info = {
            'estimator': DecisionTreeRegressor(),
            'param_grid': {'max_depth': range(4, 11)}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'DecisionTreeRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.tree import ExtraTreeRegressor
        model_info = {
            'estimator': ExtraTreeRegressor(),
            'param_grid': {'max_depth': range(4, 11)}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'ExtraTreeRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.ensemble import AdaBoostRegressor
        model_info = {
            'estimator': AdaBoostRegressor(DecisionTreeRegressor(max_depth=4)),
            'param_grid': {'n_estimators': [100, 200, 300, 500]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'AdaBoostRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.ensemble import GradientBoostingRegressor
        model_info = {
            'estimator': GradientBoostingRegressor(),
            'param_grid': {'max_depth': range(1, 6), 'n_estimators': [100, 200, 300, 500]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'GradientBoostingRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.ensemble import RandomForestRegressor
        model_info = {
            'estimator': RandomForestRegressor(),
            'param_grid': {'max_depth': range(4, 11), 'n_estimators': [100, 200, 300, 500]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'RandomForestRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.neighbors import KNeighborsRegressor
        model_info = {
            'estimator': KNeighborsRegressor(),
            'param_grid': {'n_neighbors': [3, 5, 10, 50, 100, 500]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'KNeighborsRegressor.pkl')
        save_model(clfs, pickled_filename)

        from sklearn import svm
        model_info = {
            'estimator': svm.SVR(kernel='rbf'),
            'param_grid': {'C': [0.01, 0.1, 1, 10, 100],
                           'gamma': [0.01, 0.1, 1, 10, 100]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'SVR-RBF.pkl')
        save_model(clfs, pickled_filename)

        model_info = {
            'estimator': svm.SVR(kernel='poly'),
            'param_grid': {'C': [0.01, 0.1, 1, 10, 100],
                           'degree': [2, 3, 5]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'SVR-POLY.pkl')
        save_model(clfs, pickled_filename)

        from sklearn.kernel_ridge import KernelRidge
        model_info = {
            'estimator': KernelRidge(kernel='rbf'),
            'param_grid': {'alpha': [0.01, 0.1, 1, 10],
                           'gamma': [0.01, 0.1, 1, 10, 100]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'KernelRidge-RBF.pkl')
        save_model(clfs, pickled_filename)

        model_info = {
            'estimator': KernelRidge(kernel='poly'),
            'param_grid': {'alpha': [0.01, 0.1, 1, 10],
                           'gamma': [0.01, 0.1, 1, 10, 100],
                           'degree': [2, 3, 5]}}
        clfs = train_model(dataset_name, model_info)
        pickled_filename = os.path.join(pickled_foldername, 'KernelRidge-POLY.pkl')
        save_model(clfs, pickled_filename)
