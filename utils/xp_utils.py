import os
import json

# this get our current location in the file system
import inspect
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# adding parent directory to path, so we can access the utils easily
import sys
dropfactory_path = os.path.join(HERE_PATH, '..', '..', 'dropfactory', 'software')
sys.path.append(dropfactory_path)


from tools import xp_maker

from filenaming import INFO_FILENAME
from filenaming import XP_PARAMS_FILENAME
from filenaming import XP_FEATURES_FILENAME
from filenaming import EXPLAUTO_INFO_FILENAME


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_from_json(filename):
    with open(filename) as f:
        return json.load(f)


class XPTools(object):

    def __init__(self, pool_folder):
        self.pool_folder = pool_folder

        self.info_file = os.path.join(pool_folder, INFO_FILENAME)
        if not os.path.exists(self.info_file):
            raise Exception('{} is not an experiment folder, does not contain an {} file'.format(pool_folder, INFO_FILENAME))

        self.info_dict = read_from_json(self.info_file)

        if 'environment_conf' in self.info_dict:
            self.oils_list = self.info_dict['environment_conf']['oils_list']
            self.features_list = self.info_dict['environment_conf']['features_list']

    def generate_XP_foldername(self, xp_number):
        return xp_maker.generate_XP_foldername(self.pool_folder, xp_number)

    def generate_filepath_at_xp_number(self, xp_number, filename):
        xp_folder = self.generate_XP_foldername(xp_number)
        return os.path.join(xp_folder, filename)

    def is_file_in_xp_folder(self, xp_folder, filename):
        filepath = os.path.join(xp_folder, filename)
        return os.path.exists(filepath)

    def is_file_at_xp_number(self, xp_number, filename):
        xp_folder = self.generate_XP_foldername(xp_number)
        return self.is_file_in_xp_folder(xp_folder, filename)

    def is_xp_created(self, xp_number):
        # an xp is created once the param file is out
        return self.is_file_at_xp_number(xp_number, XP_PARAMS_FILENAME)

    def is_xp_performed(self, xp_number):
        # an xp is considered done once the feature file is out
        return self.is_file_at_xp_number(xp_number, XP_FEATURES_FILENAME)

    def make_XP_dict(self, oil_ratios, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        return xp_maker.make_XP_dict(oil_ratios, xp_folder)

    def save_XP_to_xp_number(self, oil_ratios, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        self.save_XP_to_xp_folder(oil_ratios, xp_folder)

    def save_XP_to_xp_folder(self, oil_ratios, xp_folder):
        xp_maker.save_XP_to_folder(oil_ratios, xp_folder)

    def save_explauto_info_to_xp_number(self, explauto_info, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        self.save_explauto_info_to_xp_folder(explauto_info, xp_folder)

    def save_explauto_info_to_xp_folder(self, explauto_info, xp_folder):
        explauto_file = os.path.join(xp_folder, EXPLAUTO_INFO_FILENAME)
        save_to_json(explauto_info, explauto_file)

    def oils_to_params(self, oil_ratios):
        params = []
        for oil_name in self.oils_list:
            params.append(oil_ratios[oil_name])
        return params

    def params_to_oils(self, params):
        oil_names = self.oils_list
        oil_ratios = {}
        for i, oil_name in enumerate(oil_names):
            oil_ratios[oil_name] = params[i]
        return oil_ratios

    def sensors_to_features(self, sensors):
        feature_names = self.features_list
        features = {}
        for i, feature_name in enumerate(feature_names):
            features[feature_name] = sensors[i]
        return features

    def features_to_sensors(self, features):
        sensors = []
        for feature_name in self.features_list:
            sensors.append(features[feature_name])
        return sensors

    def get_XP_dict_from_xp_number(self, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        return self.get_XP_dict_from_xp_folder(xp_folder)

    def get_XP_dict_from_xp_folder(self, xp_folder):
        params_file = os.path.join(xp_folder, XP_PARAMS_FILENAME)
        return read_from_json(params_file)

    def get_params_from_xp_number(self, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        return self.get_params_from_xp_folder(xp_folder)

    def get_params_from_xp_folder(self, xp_folder):
        xp_dict = self.get_XP_dict_from_xp_folder(xp_folder)
        return self.oils_to_params(xp_dict['formulation'])

    def get_goal_from_xp_number(self, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        return self.get_goal_from_xp_folder(xp_folder)

    def get_goal_from_xp_folder(self, xp_folder):
        explauto_file = os.path.join(xp_folder, EXPLAUTO_INFO_FILENAME)
        explauto_info = read_from_json(explauto_file)
        return explauto_info['targeted_features']

    def get_sensory_from_xp_number(self, xp_number):
        xp_folder = self.generate_XP_foldername(xp_number)
        return self.get_sensory_from_xp_folder(xp_folder)

    def get_sensory_from_xp_folder(self, xp_folder):
        features_file = os.path.join(xp_folder, XP_FEATURES_FILENAME)
        features = read_from_json(features_file)
        return self.features_to_sensors(features)

    def list_file_from_xp_number(self, xp_number, filename):
        file_list = []
        for i_xp in range(xp_number, self.info_dict['n_xp_total']):
            if self.is_file_at_xp_number(i_xp, filename):
                file_list.append(self.generate_filepath_at_xp_number(i_xp, filename))
        return file_list

    def are_all_xp_done(self):
        features_files = self.list_file_from_xp_number(0, XP_FEATURES_FILENAME)
        if len(features_files) == self.info_dict['n_xp_total']:
            return True
        else:
            return False

    def delete_all_files_from_xp_number(self, xp_number, filename):
        file_list = self.list_file_from_xp_number(xp_number, filename)
        # display file found
        for f in file_list:
            print f
        # asking for purge
        response = raw_input('## Do you really want to remove all the above files [y/N]: ')
        if response in ['y', 'Y']:
            for f in file_list:
                os.remove(f)
            print 'Files have been removed'
        else:
            print 'No file removed'
