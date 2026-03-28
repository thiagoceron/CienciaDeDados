import pandas as pd

categoria = 'Eletrônicos'
df = pd.read_csv('produtos.csv') 
df_filtrado = df[df['categoria'] == categoria]

if len(df_filtrado) > 0:
    media = df_filtrado['preco'].mean()
    quantidade = len(df_filtrado)
    
    print(f"Análise da Categoria: {categoria}")
    print(f"Quantidade de itens : {quantidade}")
    print(f"Preço médio         : R$ {media:.2f}")
    
else:
    print(f"Nenhum produto encontrado na categoria '{categoria}'.")