#!/usr/bin/python

import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

##
import json
import numpy as np

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


##
from chemobot_tools.droplet_tracking.pool_workers import PoolDropletTracker
from chemobot_tools.droplet_tracking.pool_workers import PoolDropletFeatures

##
from utils import watcher

CANNY_CONFIG = {
    'blur_kernel_wh': (5, 5),
    'blur_kernel_sigma': 0,
    'dilate_kernel_wh': (2, 2),
    'canny_lower': 30,
    'canny_upper': 60,
    'noise_kernel_wh': (3, 3)
}

DISH_CONFIG = {
    'minDist': np.inf,
    'hough_config': {}
}

PROCESS_CONFIG = {
    'dish_config': DISH_CONFIG,
    'arena_ratio': 0.9,
    'canny_config': CANNY_CONFIG,
    'mog_config': {
        'learning_rate': 0.005,
        'delay_by_n_frame': 100
    }
}


VIDEO_FILENAME = 'video.avi'
VIDEO_ANALYSE_FILENAME = 'video_analysed.avi'
DROPLET_INFO_FILENAME = 'droplet_info.json'
DISH_INFO_FILENAME = 'dish_info.json'
DROPLET_FEATURES_FILENAME = 'droplet_features.json'
FEATURES_FILENAME = 'features.json'


def create_tracker_config(foldername, debug=True):
    tracker_config = {
        'video_filename': os.path.join(foldername, VIDEO_FILENAME),
        'process_config': PROCESS_CONFIG,
        'video_out': os.path.join(foldername, VIDEO_ANALYSE_FILENAME),
        'droplet_info_out': os.path.join(foldername, DROPLET_INFO_FILENAME),
        'dish_info_out': os.path.join(foldername, DISH_INFO_FILENAME),
        'debug': debug,
        'debug_window_name': os.path.basename(foldername),
        'verbose': True
    }
    return tracker_config


def create_features_config(foldername):
    features_config = {
        'dish_info_filename': os.path.join(foldername, DISH_INFO_FILENAME),
        'droplet_info_filename': os.path.join(foldername, DROPLET_INFO_FILENAME),
        'max_distance_tracking': 40,
        'min_sequence_length': 20,
        'dish_diameter_mm': 32,
        'frame_per_seconds': 20,
        'features_out': os.path.join(foldername, DROPLET_FEATURES_FILENAME),
        'verbose': True
    }
    return features_config


def compile_features(droplet_features):
    features = {}
    features['lifetime'] = droplet_features['ratio_frame_active']
    features['speed'] = droplet_features['average_speed']
    features['wobble'] = droplet_features['average_perimeter_variation']
    return features


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    import multiprocessing
    n_jobs = multiprocessing.cpu_count()
    # n_jobs = 1

    # video
    droptracker = PoolDropletTracker(n_jobs)

    def add_video_for_analysis(folder, watch_file):
        print '###\nAdding {} for video analysis'.format(watch_file)
        droptracker.add_task(create_tracker_config(folder))

    video_watcher = watcher.Watcher(pool_folder, VIDEO_FILENAME, DROPLET_INFO_FILENAME, add_video_for_analysis, force=False)

    # droplet_features
    dropfeatures = PoolDropletFeatures(n_jobs)

    def add_droplet_info_for_feature_extraction(folder, watch_file):
        print '###\nAdding {} for feature extraction'.format(watch_file)
        dropfeatures.add_task(create_features_config(folder))

    drop_feature_watcher = watcher.Watcher(pool_folder, DROPLET_INFO_FILENAME, DROPLET_FEATURES_FILENAME, add_droplet_info_for_feature_extraction, force=False)
    # algortihm feature

    def features_for_algo(folder, watch_file):
        print '###\nGetting features from  {}...'.format(watch_file)
        droplet_features = read_from_json(watch_file)
        features = compile_features(droplet_features)
        features_file = os.path.join(folder, FEATURES_FILENAME)
        save_to_json(features, features_file)
        print '###\nFeatures extracted from  {}.'.format(watch_file)

    feature_watcher = watcher.Watcher(pool_folder, DROPLET_FEATURES_FILENAME, FEATURES_FILENAME, features_for_algo, force=False)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        video_watcher.join()
        drop_feature_watcher.join()
        feature_watcher.join()
