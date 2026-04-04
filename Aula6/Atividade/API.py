import requests
import pandas as pd

url_real = "https://jsonplaceholder.typicode.com/users"

resposta = requests.get(url_real)

if resposta.status_code == 200:
    dados = resposta.json()
    df_teste = pd.DataFrame(dados)
    
    print("DataFrame gerado da API\n")
    print(df_teste[['id', 'name', 'email', 'phone']])
else:
    print("Erro")