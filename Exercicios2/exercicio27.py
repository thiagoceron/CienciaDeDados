import numpy as np

array = np.random.randint(0, 101, 10)

print(array)

mascara = array > 50
print(mascara)

print("Valores que sao maiores que 50")
print(array[(array > 50)])