import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

def extrair_e_converter(parametros):
    arquivo = parametros["entrada"]
    df = pd.read_csv(arquivo, sep=",", encoding="utf-8", low_memory=False)

    col_tempo = parametros["coluna_tempo"]
    col_metrica = parametros["coluna_metrica"]

    df["ano_formatado"] = df[col_tempo].astype(str).str[:4]
    df["ano_formatado"] = pd.to_numeric(df["ano_formatado"], errors="coerce")
    df[col_metrica] = pd.to_numeric(df[col_metrica], errors="coerce")

    df_limpo = df.dropna(subset=["ano_formatado", col_metrica]).copy()

    caminho_json = parametros["saida_json"]
    df_limpo.head(150).to_json(caminho_json, orient="records", force_ascii=False, indent=4)
    print(f"Arquivo: {caminho_json}")

    return df_limpo

def aplicar_filtro_temporal(df, parametros):
    limite_anos = parametros["filtro_anos"]
    
    ano_referencia = datetime.now().year
    
    if df[df["ano_formatado"] >= (ano_referencia - limite_anos)].empty:
        ano_referencia = int(df["ano_formatado"].max())
        
    ano_corte = ano_referencia - limite_anos
    df_recortado = df[df["ano_formatado"] >= ano_corte].copy()
    
    print(f"Filtro temporal aplicado: a partir de {ano_corte}")
    return df_recortado

def extrair_metricas_basicas(df, parametros):
    alvo = parametros["coluna_metrica"]
    
    resultados = {
        "Media": df[alvo].mean(),
        "Maximo": df[alvo].max(),
        "Minimo": df[alvo].min()
    }
    return resultados

def plotar_dashboards(df, parametros):
    ano = "ano_formatado"
    metrica = parametros["coluna_metrica"]
    categoria = parametros["coluna_categoria"]
    
    plt.style.use("bmh")
    fig, (grafico1, grafico2) = plt.subplots(1, 2, figsize=(14, 6))

    agrupamento_anual = df.groupby(ano)[metrica].sum()
    grafico1.plot(agrupamento_anual.index, agrupamento_anual.values, color="darkred", marker="s", linewidth=2)
    grafico1.set_title("Volume de Mamografias ao Longo do Tempo")
    grafico1.set_xlabel("Ano")
    grafico1.set_ylabel("Quantidade Indicador")

    agrupamento_estadual = df.groupby(categoria)[metrica].sum().nlargest(10).sort_values()
    grafico2.barh(agrupamento_estadual.index, agrupamento_estadual.values, color="steelblue", edgecolor="black")
    grafico2.set_title("10 Estados com Maior Volume Registrado")
    grafico2.set_xlabel("Quantidade Total")
    grafico2.set_ylabel("UF")

    plt.tight_layout()
    plt.savefig(parametros["saida_grafico"], dpi=120)
    plt.close()
    print(f"Visualizacoes para: {parametros['saida_grafico']}")

def banco_relacional(df, parametros):
    db = parametros["banco_dados"]
    tabela = parametros["tabela_dados"]
    
    conexao = sqlite3.connect(db)
    df.to_sql(tabela, conexao, if_exists="replace", index=False)
    conexao.close()
    print(f"Registros salvos no SQLite ({db})")

def iniciar_pipeline():
    configuracoes = {
        "entrada": "mamografia.csv",
        "coluna_tempo": "co_anomes",
        "coluna_metrica": "vl_indicador_calculado_mun",
        "coluna_categoria": "sg_uf",
        "filtro_anos": 10,
        "saida_json": "exportacao_mamografia.json",
        "saida_grafico": "graficos.png",
        "banco_dados": "sistema_saude.db",
        "tabela_dados": "historico_mamografias"
    }

    dados_brutos = extrair_e_converter(configuracoes)
    dados_processados = aplicar_filtro_temporal(dados_brutos, configuracoes)
    
    estatisticas = extrair_metricas_basicas(dados_processados, configuracoes)
    
    print("\nResultados: ")
    for chave, valor in estatisticas.items():
        print(f"  {chave}: {valor:,.2f}")
    print("\n")

    plotar_dashboards(dados_processados, configuracoes)
    banco_relacional(dados_processados, configuracoes)

if __name__ == "__main__":
    iniciar_pipeline()