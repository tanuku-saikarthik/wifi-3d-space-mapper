import numpy as np

def mds(dist, prev=None, iters=4):
    n = len(dist)
    if prev is None:
        Y = np.random.randn(n, 3) * 5
    else:
        Y = prev.copy()

    for _ in range(iters):
        for i in range(n):
            force = np.zeros(3)
            for j in range(n):
                if i == j: continue
                d = np.linalg.norm(Y[i] - Y[j]) + 1e-6
                force += (d - dist[i][j]) * (Y[i] - Y[j]) / d
            Y[i] -= 0.01 * force
    return Y
