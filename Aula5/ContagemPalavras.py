import pandas as pd
import string

caminho_arquivo = 'arquivo.txt'

with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
    conteudo = arquivo.read().lower()

tabela_pontuacao = str.maketrans('', '', string.punctuation)
texto_limpo = conteudo.translate(tabela_pontuacao)
palavras = texto_limpo.split()

serie_palavras = pd.Series(palavras)
top_10 = serie_palavras.value_counts().head(10)

print(f"{'Palavra':<15} | {'Frequência':<10}")

for palavra, freq in top_10.items():
    print(f"{palavra:<15} | {freq:<10}")