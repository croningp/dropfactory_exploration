import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..')
sys.path.append(root_path)

##
import time
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
from chemobot_tools.droplet_tracking.droplet_feature import compute_droplet_features
from chemobot_tools.droplet_classification.droplet_classifier import DropletClassifier

##
from utils import watcher

from utils.filenaming import VIDEO_FILENAME
from utils.filenaming import VIDEO_ANALYSE_FILENAME
from utils.filenaming import VIDEO_TRACK_FILENAME
from utils.filenaming import DROPLET_INFO_FILENAME
from utils.filenaming import DISH_INFO_FILENAME
from utils.filenaming import DROPLET_FEATURES_FILENAME
from utils.filenaming import XP_FEATURES_FILENAME


DISH_CONFIG = {
    'minDist': np.inf,
    'hough_config': {},
    'dish_center': None,
    'dish_radius': 180
}

CANNY_CONFIG = {
    'blur_kernel_wh': (5, 5),
    'blur_kernel_sigma': 0,
    'dilate_kernel_wh': (2, 2),
    'canny_lower': 30,
    'canny_upper': 60,
    'noise_kernel_wh': (3, 3)
}

CANNY_HYPOTHESIS_CONFIG = {
    'canny_config': CANNY_CONFIG,
    'width_ratio': 1.5
}

HOUGH_CONFIG = {
    'minDist': 5,
    'hough_config': {
        'param1':80,
        'param2':5,
        'minRadius':5,
        'maxRadius':30
    },
    'max_detected': 20
}

HOUGH_HYPOTHESIS_CONFIG = {
    'hough_config': HOUGH_CONFIG,
    'width_ratio': 1.5
}

BLOB_CONFIG = {
    'minThreshold': 10,
    'maxThreshold': 200,
    'filterByArea': True,
    'minArea': 50,
    'filterByCircularity': True,
    'minCircularity': 0.1,
    'filterByConvexity': True,
    'minConvexity': 0.8,
    'filterByInertia': True,
    'minInertiaRatio': 0.01,
}

BLOB_HYPOTHESIS_CONFIG = {
    'blob_config': BLOB_CONFIG,
    'width_ratio': 1.5
}

MOG_HYPOTHESIS_CONFIG = {
    'learning_rate': 0.005,
    'delay_by_n_frame': 100,
    'width_ratio': 1.5
}


DROPLET_CLASSIFIER = DropletClassifier.from_folder(os.path.join(HERE_PATH, 'classifier_info'))

HYPOTHESIS_CONFIG = {
    'droplet_classifier': DROPLET_CLASSIFIER,
    'class_name': 'droplet'
}

PROCESS_CONFIG = {
    'dish_detect_config': DISH_CONFIG,
    'dish_frame_spacing': 20,
    'arena_ratio': 0.8,
    'canny_hypothesis_config': CANNY_HYPOTHESIS_CONFIG,
    'hough_hypothesis_config': HOUGH_HYPOTHESIS_CONFIG,
    'blob_hypothesis_config': BLOB_HYPOTHESIS_CONFIG,
    'mog_hypothesis_config': MOG_HYPOTHESIS_CONFIG,
    'resolve_hypothesis_config': HYPOTHESIS_CONFIG
}


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


def create_features_config(foldername, debug=True):
    features_config = {
        'dish_info_filename': os.path.join(foldername, DISH_INFO_FILENAME),
        'droplet_info_filename': os.path.join(foldername, DROPLET_INFO_FILENAME),
        'max_distance_tracking': 40,
        'min_sequence_length': 20,
        'join_min_frame_dist': 1,
        'join_max_frame_dist': 10,
        'min_droplet_radius': 5,
        'dish_diameter_mm': 28,
        'frame_per_seconds': 20,
        'features_out': os.path.join(foldername, DROPLET_FEATURES_FILENAME),
        'video_in': os.path.join(foldername, VIDEO_FILENAME),
        'video_out': os.path.join(foldername, VIDEO_TRACK_FILENAME),
        'debug': debug,
        'debug_window_name': os.path.basename(foldername),
        'verbose': True
    }
    return features_config


SCALAR_LIFETIME = 1.
SCALAR_SPEED = 1./20.
SCALAR_WOBBLE = 5.

def compile_features(droplet_features):
    features = {}
    features['lifetime'] = SCALAR_LIFETIME * droplet_features['ratio_frame_active']
    features['speed'] = SCALAR_SPEED * droplet_features['average_speed']
    features['wobble'] = SCALAR_WOBBLE * droplet_features['median_absolute_circularity_deviation']
    return features


def is_file_busy(filename, modified_time=1):
    """
    Find if a file was modified in the last x seconds given by modified_time.
    """
    time_start = os.stat(filename).st_mtime # Time file last modified
    time.sleep(modified_time)               # wait modified_time for secs
    time_end = os.stat(filename).st_mtime   # File modification time again
    return time_end > time_start


if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print 'Please specify pool_folder as argument'

    pool_folder = os.path.join(HERE_PATH, sys.argv[1])

    # video
    n_cores = 3
    droptracker = PoolDropletTracker(n_cores)

    def add_video_for_analysis(folder, watch_file):
        while is_file_busy(watch_file):
            pass  # look weird but is_file_busy is already sleeping some

        print '###\nAdding {} for video analysis'.format(watch_file)
        droptracker.add_task(create_tracker_config(folder))

    video_watcher = watcher.Watcher(pool_folder, VIDEO_FILENAME, DROPLET_INFO_FILENAME, add_video_for_analysis, force=False)

    # droplet_features
    def droplet_info_to_droplet_features(folder, watch_file):

        while is_file_busy(watch_file):
            pass  # look weird but is_file_busy is already sleeping some

        config = create_features_config(folder)

        dish_info_filename = config['dish_info_filename']
        del config['dish_info_filename']

        droplet_info_filename = config['droplet_info_filename']
        del config['droplet_info_filename']

        compute_droplet_features(dish_info_filename, droplet_info_filename, **config)

    drop_feature_watcher = watcher.Watcher(pool_folder, DROPLET_INFO_FILENAME, DROPLET_FEATURES_FILENAME, droplet_info_to_droplet_features, force=False)


    # algortihm feature
    def features_for_algo(folder, watch_file):
        while is_file_busy(watch_file):
            pass  # look weird but is_file_busy is already sleeping some

        print '###\nGetting features from  {}...'.format(watch_file)
        droplet_features = read_from_json(watch_file)
        features = compile_features(droplet_features)
        features_file = os.path.join(folder, XP_FEATURES_FILENAME)
        save_to_json(features, features_file)
        print '###\nFeatures extracted from  {}.'.format(watch_file)

    feature_watcher = watcher.Watcher(pool_folder, DROPLET_FEATURES_FILENAME, XP_FEATURES_FILENAME, features_for_algo, force=False)

    # this is better into ipython for more flexibility
    try:
        __IPYTHON__
    except NameError:
        print 'Not running in ipython :( -> blocking the ending till you ctrl-c'
        video_watcher.join()
        drop_feature_watcher.join()
        feature_watcher.join()
