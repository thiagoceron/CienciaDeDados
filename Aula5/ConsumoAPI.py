import requests


topico = "data science"
url = f"https://api.github.com/search/repositories?q={topico}"

print(f"Buscando repositórios sobre '{topico}' no GitHub\n")
resposta = requests.get(url)
dados = resposta.json()
repositorios = dados.get('items', [])

if len(repositorios) > 0:
    print(f"{'NOME DO REPOSITÓRIO':<30} | URL")
    top_5 = repositorios[:5]
    
    for repo in top_5:
        nome = repo['name']
        link = repo['html_url']
        print(f"{nome:<30} | {link}")
else:
    print(f"Nenhum repositório encontrado ou limite da API atingido.")