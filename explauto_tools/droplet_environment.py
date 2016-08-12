import numpy as np

from explauto import Environment
from explauto.utils import bounds_min_max


SCALE_VALUE = [24, 18, 5]
# to understand the scale value, you should know that the dataset used for the model we use is dereived from the 'octanoic' dataset
# you can do something like this to load it:
# from datasets.tools import load_dataset
# X, y, info, path = load_dataset('octanoic')
# the root of using [24, 18, 5] come from the max values in y, check for yourself: print np.max(y, axis=0)
# which should give [ 24., 17.9254319 , 4.99090837]


def proba_normalize(x):
    x = np.array(x, dtype=float)
    if np.sum(x) == 0:
        x = np.ones(x.shape)
    return x / np.sum(x, dtype=float)


class DropletEnvironment(Environment):
    use_process = False

    def __init__(self, m_mins, m_maxs, s_mins, s_maxs, out_dims, clf, scale_prediction=True, scale_value=SCALE_VALUE):
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)
        self.clf = clf
        self.out_dims = out_dims
        self.scale_prediction = scale_prediction
        self.scale_value = scale_value

    def compute_motor_command(self, m_ag):
        m_ag = bounds_min_max(m_ag, self.conf.m_mins, self.conf.m_maxs)
        return proba_normalize(m_ag)

    def compute_sensori_effect(self, m_env):
        m_env = np.atleast_1d(m_env)
        s_env = self.clf.predict(m_env)[:, self.out_dims]

        if self.scale_prediction:
            # we 'normalize for out to be betwenen 0 and 1 in each dimension'
            s_env = s_env / self.scale_value

        if len(m_env.shape) == 1:
            return s_env.reshape((s_env.size, ))
        else:
            return s_env
