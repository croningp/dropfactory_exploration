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
from chemobot_tools.droplet_tracking.pool_workers import PoolSimpleDropletTracker
from chemobot_tools.droplet_tracking.pool_workers import PoolDropletFeatures

##
from utils import watcher

from utils.filenaming import VIDEO_FILENAME
from utils.filenaming import VIDEO_ANALYSE_FILENAME
from utils.filenaming import VIDEO_TRACK_FILENAME
from utils.filenaming import DROPLET_INFO_FILENAME
from utils.filenaming import DISH_INFO_FILENAME
from utils.filenaming import DROPLET_FEATURES_FILENAME
from utils.filenaming import XP_FEATURES_FILENAME
from utils.filenaming import BINARIZATION_THRESHOLD_FILENAME


def create_tracker_config(foldername, debug=True):
    DISH_CONFIG = {
        'minDist': np.inf,
        'hough_config': {},
        'dish_center': None,
        'dish_radius': 200
    }

    BINARIZATION_THRESHOLD_CONFIG = {
        'cut_proba': 0.001,
        'spectrum_filename': os.path.join(foldername, BINARIZATION_THRESHOLD_FILENAME)
    }

    PROCESS_CONFIG = {
        'dish_detect_config': DISH_CONFIG,
        'dish_frame_spacing': 20,
        'arena_ratio': 0.8,
        'binarization_threshold_config': BINARIZATION_THRESHOLD_CONFIG
    }

    tracker_config = {
        'video_filename': os.path.join(foldername, VIDEO_FILENAME),
        'process_config': PROCESS_CONFIG,
        'video_out': None,
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
        'max_distance_tracking': 100,
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

SCALAR_SPEED = 1./20.
SCALAR_DEFORMATION = 5.
SCALAR_DIVISION = 1./20.
SCALAR_LIFETIME = 1.
SCALAR_COVERAGE = 1.

def compile_features(droplet_features):
    features = {}
    features['speed'] = SCALAR_SPEED * droplet_features['average_speed']
    features['deformation'] = SCALAR_DEFORMATION * droplet_features['median_absolute_circularity_deviation']
    features['division'] = SCALAR_DIVISION * droplet_features['average_number_of_droplets']
    features['lifetime'] = SCALAR_LIFETIME * droplet_features['ratio_frame_active']
    features['coverage'] = SCALAR_COVERAGE * droplet_features['covered_arena_area']
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

    if not os.path.exists(pool_folder):
        raise Exception('The folder does not exists: {}!'.format(pool_folder))

    n_cores = 6

    # video
    droptracker = PoolSimpleDropletTracker(n_cores)

    def add_video_for_analysis(folder, watch_file):
        while is_file_busy(watch_file):
            pass  # look weird but is_file_busy is already sleeping some

        print '###\nAdding {} for video analysis'.format(watch_file)
        droptracker.add_task(create_tracker_config(folder))

    video_watcher = watcher.Watcher(pool_folder, VIDEO_FILENAME, DROPLET_INFO_FILENAME, add_video_for_analysis, force=False)

    # droplet_features
    dropfeatures = PoolDropletFeatures(n_cores)

    def droplet_info_to_droplet_features(folder, watch_file):

        while is_file_busy(watch_file):
            pass  # look weird but is_file_busy is already sleeping some

        dropfeatures.add_task(create_features_config(folder))

    drop_feature_watcher = watcher.Watcher(pool_folder, DROPLET_INFO_FILENAME, DROPLET_FEATURES_FILENAME, droplet_info_to_droplet_features, force=False)


    # algorithm feature
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
