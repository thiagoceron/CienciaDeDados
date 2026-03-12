import numpy as np

arr = np.arange(10)

print(arr)

arr[arr % 2 != 0] = -1

print(arr)

