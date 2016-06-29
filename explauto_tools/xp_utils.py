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


XP_PARAMS_FILENAME = 'params.json'
XP_FEATURES_FILENAME = 'features.json'
INFO_FILENAME = 'info.json'
EXPLAUTO_INFO_FILENAME = 'explauto_info.json'


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
        self.info_dict = read_from_json(self.info_file)

        self.oils_list = self.info_dict['environment_conf']['oils_list']
        self.features_list = self.info_dict['environment_conf']['features_list']

    def generate_XP_foldername(self, xp_number):
        return xp_maker.generate_XP_foldername(self.pool_folder, xp_number)

    def is_xp_created(self, xp_number):
        # an xp is created once the param file is out
        xp_folder = self.generate_XP_foldername(xp_number)
        param_file = os.path.join(xp_folder, XP_PARAMS_FILENAME)
        return os.path.exists(param_file)

    def is_xp_performed(self, xp_number):
        # an xp is considered done once the feature file is out
        xp_folder = self.generate_XP_foldername(xp_number)
        feature_file = os.path.join(xp_folder, XP_FEATURES_FILENAME)
        return os.path.exists(feature_file)

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
