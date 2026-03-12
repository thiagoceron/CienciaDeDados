import numpy as np

array = np.arange(10)

print(array)

print("Numeros pares: ")

print(array[array[array % 2 == 0]])