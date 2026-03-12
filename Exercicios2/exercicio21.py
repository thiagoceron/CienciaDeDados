import numpy as np

array = np.array([1, 2, 2, 3, 4, 4, 4, 5])

print(array)

valores, contagem = np.unique(array, return_counts=True)

unico = valores[contagem ==1]

print("Valores Unicos: ", unico)