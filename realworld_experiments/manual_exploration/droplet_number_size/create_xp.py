import os

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
root_path = os.path.join(HERE_PATH, '..', '..', '..')
sys.path.append(root_path)

dropfactory_path = os.path.join(root_path, '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)

from tools.filenaming import XP_PARAMS_FILENAME
from tools.xp_maker import RUN_INFO_FILENAME
from tools.xp_maker import VIDEO_FILENAME
from tools.xp_maker import generate_XP_foldername

from utils.xp_utils import save_to_json

DROPLET_PLACEMENT_RADIUS_MM = 5
POSITION_LIST = [[5,0], [-5,0], [0,5], [0,-5]]
EXPERIMENT_FOLDER = os.path.join(HERE_PATH, 'experiments')


def build_xp_dict(xp_folder, oil_ratios, droplet_number, droplet_volume_uL):

    XP_dict = {
        'min_waiting_time': 60,
        'surfactant_volume': 3.5,
        'video_info': {
            'filename': os.path.join(xp_folder, VIDEO_FILENAME),
            'duration': 90
        },
        'run_info': {
            'filename': os.path.join(xp_folder, RUN_INFO_FILENAME)
        },
        'formulation': {},
        'droplets': []
    }

    oil_names = ['octanol', 'octanoic', 'pentanol', 'dep']
    for oil_name in oil_names:
        XP_dict['formulation'][oil_name] = oil_ratios[oil_name]

    pos_id = 0
    for _ in range(droplet_number):

        drop_info = {}
        # volume are all the same
        drop_info['volume'] = droplet_volume_uL
        # positions alternate
        if droplet_number == 1:
            drop_info['position'] = [0, 0]
        else:
            drop_info['position'] = POSITION_LIST[pos_id]
        XP_dict['droplets'].append(drop_info)

        pos_id += 1
        if pos_id == len(POSITION_LIST):
            pos_id = 0

    return XP_dict


def forge_xp_folder(formulation_name, droplet_number, droplet_volume_uL, i_repeat, n_digit=2):

    formulation_folder = os.path.join(EXPERIMENT_FOLDER, formulation_name)

    str_n_droplet = str(droplet_number).zfill(n_digit)
    str_drop_volume = str(droplet_volume_uL).zfill(n_digit)
    str_repeat = str(i_repeat).zfill(n_digit)
    fname = 'N{}_V{}_{}'.format(str_n_droplet, str_drop_volume, str_repeat)

    return os.path.join(formulation_folder, fname)


if __name__ == '__main__':

    import filetools

    DROPLET_NUMBERS = [1, 4, 12]
    DROPLET_VOLUMES = [1, 2, 4, 8]
    N_REPEATS = 5

    formulation_name = 'speed'

    oil_ratios = {
        "dep": 0.37,
        "octanol": 0.30,
        "octanoic": 0.0,
        "pentanol": 0.33
    }

    for droplet_number in DROPLET_NUMBERS:
        for droplet_volume_uL in DROPLET_VOLUMES:
            for i_repeat in range(N_REPEATS):

                xp_folder = forge_xp_folder(formulation_name, droplet_number, droplet_volume_uL, i_repeat)
                param_filename = os.path.join(xp_folder, XP_PARAMS_FILENAME)

                XP_dict = build_xp_dict(xp_folder, oil_ratios, droplet_number, droplet_volume_uL)

                if not os.path.exists(param_filename):
                    filetools.ensure_dir(xp_folder)
                    save_to_json(XP_dict, param_filename)
                else:
                    print 'Skipping {}, it already exists'.format(param_filename)
