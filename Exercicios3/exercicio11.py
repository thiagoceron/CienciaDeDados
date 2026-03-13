import pandas as pd

for bloco in pd.read_csv('dados_sensor_gigante.csv', chunksize=10):
    media_temperatura = bloco["temperatura"].mean()
    valores_ausentes = bloco["temperatura"].isna().sum()
    print(bloco)
    print("Temperatura média:", media_temperatura)
    print("Valores ausentes na temperatura:", valores_ausentes)