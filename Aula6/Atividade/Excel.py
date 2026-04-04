import pandas as pd

dados = {'Departamento': ['Vendas', 'TI', 'RH'], 'Lucro': [50000, 80000, 20000]}
relatorio_anual = pd.DataFrame(dados)

relatorio_anual.to_excel('relatorio.xlsx', sheet_name='Resultados', index=False)
print("relatorio.xlsx criado")

df_dados_brutos = pd.read_excel('arquivo_existente.xlsx', sheet_name='Dados Brutos')
print("\nLeitura realizada do arquivo existente: ")

print(df_dados_brutos)