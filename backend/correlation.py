import numpy as np

def pearson(a, b):
    if a is None or b is None:
        return 0.0
    n = min(len(a), len(b))
    if n < 2:
        return 0.0
    return float(np.corrcoef(a[-n:], b[-n:])[0,1])

def corr_to_dist(r):
    return np.sqrt(max(0.0, 2 * (1 - r)))
