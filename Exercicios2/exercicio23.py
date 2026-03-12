import numpy as np

notas = np.array([80, 90, 70] )
pesos = np.array([0.3, 0.5, 0.2])

print("Notas: ", notas)
print("Pesos: ", pesos)

somaPesos = np.sum(pesos)
multiplicar = (notas * pesos)
somaResultados = np.sum(multiplicar)
mediaPonderada = somaResultados / somaPesos

print("Media Ponderada: ", mediaPonderada)