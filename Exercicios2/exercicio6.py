import numpy as np

arr = np.random.randint(1,100,(5,5))

print(arr)
print("Soma das colunas: ", arr.sum(axis=0))
