import pandas as pd

df_vendas = pd.read_csv('vendas.csv', header=None, index_col=0, na_values=['ND'])     

df_vendas.columns = ['Data', 'Produto', 'Quantidade', 'Valor_Unitario']

print(df_vendas)
print("\nValores nulos detectados por coluna:")
print(df_vendas.isna().sum())