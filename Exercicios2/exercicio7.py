import numpy as np

arr = np.random.randint(1,100,(5,5))

print(arr)
print("Valor maximo de cada linha: ", arr.max(axis=1))