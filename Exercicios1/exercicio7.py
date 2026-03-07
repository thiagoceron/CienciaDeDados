from collections import Counter

frase = "O presente não é um passado em potência, ele é o momento da escolha e da ação"
print(frase)

palavras = frase.lower().split()
cont = Counter(palavras)
top3 = cont.most_common(3)

print("As 3 palavras mais frequentes sao: ")
for palavras, qtd in top3:
    print(f"{palavras}: {qtd}")

