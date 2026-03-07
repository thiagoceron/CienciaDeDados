Contato = {
    "Thiago Ceron" : "43 999813686",
    "Eduardo Larson" : "43 939872373",
    "Joao luy" : "43 939872323",
}

for nome, telefone in Contato.items():
    print(nome)

busca = input("Digite o nome que voce quer buscar")

if busca in Contato:
    print(f"Telefone de {busca}: {Contato[busca]}")
else:
    print(f"Contato {busca} nao encontrado")    
