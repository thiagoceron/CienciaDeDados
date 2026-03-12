import numpy as np

array = np.array([1, 7, 3, 7, 5, 7, 7, 7])
print(array)

igual_7 =  array[array == 7]

print(f"Contagem de 7: ",len(igual_7))
