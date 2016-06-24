import numpy as np

from explauto import Environment
from explauto.utils import bounds_min_max


def proba_normalize(x):
    x = np.array(x, dtype=float)
    if np.sum(x) == 0:
        x = np.ones(x.shape)
    return x / np.sum(x, dtype=float)


class DropletEnvironment(Environment):
    use_process = False

    def __init__(self, m_mins, m_maxs, s_mins, s_maxs, out_dims, clf):
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)
        self.clf = clf
        self.out_dims = out_dims

    def compute_motor_command(self, m_ag):
        m_ag = bounds_min_max(m_ag, self.conf.m_mins, self.conf.m_maxs)
        return proba_normalize(m_ag)

    def compute_sensori_effect(self, m_env):
        m_env = np.atleast_1d(m_env)
        s_env = self.clf.predict(m_env)[:, self.out_dims]
        if len(m_env.shape) == 1:
            return s_env.reshape((s_env.size, ))
        else:
            return s_env
