import numpy as np

array = np.random.randint(0 , 10, (3,4))

print(array)

inverter = np.flip(array, axis=0)

print("Matriz invertida na primeira linha com a ultima: ")
print(inverter)