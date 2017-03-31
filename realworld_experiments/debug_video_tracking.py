import os

from vision_watch_folder import create_tracker_config
from chemobot_tools.droplet_tracking.simple_droplet_tracker import process_video

from vision_watch_folder import create_features_config
from chemobot_tools.droplet_tracking.droplet_feature import compute_droplet_features


foldername = '/home/group/workspace/dropfactory_exploration/realworld_experiments/random_params/112/00860/'

# config = create_tracker_config(foldername)
# config['deep_debug'] = False
# process_video(**config)

config = create_features_config(foldername)
compute_droplet_features(**config)
