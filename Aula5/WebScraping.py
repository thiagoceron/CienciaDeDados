import requests
from bs4 import BeautifulSoup

url = 'https://classofficial.com.br/'
resposta = requests.get(url)
soup = BeautifulSoup(resposta.text, 'html.parser')
titulos_h2 = soup.find_all('h2')

print(f"Buscando <h2> no site: {url}\n")

if len(titulos_h2) > 0:
    for titulo in titulos_h2:
        texto_limpo = titulo.text.strip()
        if len(texto_limpo) > 0:
            print(f"-> {texto_limpo}")
else:
    print("Nenhuma tag <h2> foi encontrada.")
