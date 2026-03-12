import numpy as np
np.set_printoptions(precision=2, suppress=True)

matriz = np.random.randint(100,500,size=(3,4))

print("Matriz Aleatoria: ", matriz)
print("Venda total por semana: ", matriz.sum(axis=1) )
print(f"Media das colunas: ", matriz.mean(axis=0))
print("Dias superiores a 400: ", matriz[matriz>400])