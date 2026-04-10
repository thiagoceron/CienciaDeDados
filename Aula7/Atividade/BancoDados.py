import pandas as pd
from sqlalchemy import create_engine


dados = pd.DataFrame({
    'ID_Produto': [1, 2, 3, 4, 5],
    'Nome': ['Notebook', 'Mouse', 'Teclado', 'Monitor', 'Cabo HDMI'],
    'Preco': [3500.00, 45.00, 120.50, 800.00, 15.00],
    'Estoque': [10, 50, 30, 15, 100]
})

engine_setup = create_engine('sqlite:///meu_banco.db')
dados.to_sql('produtos', con=engine_setup, index=False, if_exists='replace')

print("Banco de dados criado\n")

engine = create_engine('sqlite:///meu_banco.db')
df_produtos = pd.read_sql('produtos', con=engine)


print("Dados do banco de dados: ")
print(df_produtos)