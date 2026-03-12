import numpy as np

array = np.random.rand(20)

print(array)

maior = array[array > 0.7]

print(f"Maiores que 0.7: ",maior)  
