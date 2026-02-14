import numpy as np
from collections import deque

WINDOW = 20
ALPHA = 0.3

class SignalBuffer:
    def __init__(self):
        self.values = deque(maxlen=WINDOW)
        self.ewma = None

    def add(self, rssi):
        if self.ewma is None:
            self.ewma = rssi
        else:
            self.ewma = ALPHA * rssi + (1 - ALPHA) * self.ewma
        self.values.append(self.ewma)

    def zscore(self):
        if len(self.values) < 2:
            return None
        x = np.array(self.values)
        return (x - x.mean()) / (x.std() + 1e-6)

    def variance(self):
        if len(self.values) < 2:
            return 1.0
        return np.var(self.values)
    