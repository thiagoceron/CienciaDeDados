import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

concatenacao = np.hstack((a, b))
print(concatenacao)