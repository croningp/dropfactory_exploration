import os

from vision_watch_folder import create_tracker_config
from chemobot_tools.droplet_tracking.simple_droplet_tracker import process_video
from chemobot_tools.droplet_tracking.pool_workers import PoolSimpleDropletTracker

# pool
n_cores = 6
droptracker = PoolSimpleDropletTracker(n_cores)

for i in range(47, 48):

    foldername = '/home/group/workspace/dropfactory/software/test_pool_folder/000{}'.format(i)

    config = create_tracker_config(foldername)
    config['deep_debug'] = False

    # one by one
    process_video(**config)

    # pool
    # droptracker.add_task(config)

droptracker.wait_until_idle()
