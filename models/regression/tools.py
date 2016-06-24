import pickle
import numpy as np


def load_model(filename):
    clfs = pickle.load(open(filename))
    return Model(clfs)


class Model(object):

    def __init__(self, clfs):
        self.model = clfs

    def predict(self, x, out_dims=None):
        x = np.atleast_2d(x)

        if out_dims is None:
            out_dims = range(len(self.model))
        else:
            if type(out_dims) == int:
                out_dims = [out_dims]

        output = np.zeros((x.shape[0], len(out_dims)))
        for i, row in enumerate(x):
            for j, dim in enumerate(out_dims):
                output[i, j] = self.model[dim].predict(row)

        return output
