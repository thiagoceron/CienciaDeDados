import numpy as np

array = np.array([120.50, 121.00, 119.80, 122.30, 120.00])

print(array)

variacao = (array[1:] - array[:-1]) / array[:-1] * 100

print("Variação percentual díaria: ", variacao)