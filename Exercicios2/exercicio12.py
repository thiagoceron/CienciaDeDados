import numpy as np

array = np.random.randint(50,201,(3,4))

print("Vendas: " , array)

total = np.sum(array, axis=1)

print("Total de vendas dos produtos: ", total)