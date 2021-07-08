import numpy as np

def line_length(signal):
    return np.sum(np.abs(np.diff(signal)))