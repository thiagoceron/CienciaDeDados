pontoA = (1,2)
pontoB = (3, 5)

def distancia_euclidiana(pA, pB):
    return ((pB[0] - pA[0]) ** 2 + (pB[1] - pA[1] ** 2) ** 0.5)
distancia = distancia_euclidiana (pontoA, pontoB)
print(f"A distancia entre pontos A {pontoA} e B {pontoB} é {distancia:.2f}")