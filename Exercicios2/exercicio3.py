import numpy as np  

arr = np.arange(10)

print(arr)

impares = arr[arr % 2 != 0]
print(impares)