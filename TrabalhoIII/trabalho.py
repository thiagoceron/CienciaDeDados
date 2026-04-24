import pandas as pd
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import os


def coletar_dados(caminho_csv):
    print("Pegando arquivo mamografia.csv")
    
    if not os.path.exists(caminho_csv):
        print(f"Arquivo '{caminho_csv}' não encontrado.")
        return None

    try:
        df = pd.read_csv(caminho_csv, sep=',', encoding='utf-8')
        print(f"Arquivo deu bom")
        print(f"    Registros encontrados: {len(df)}")
        print(f"    Colunas disponíveis: {list(df.columns)}\n")
        return df

    except Exception as e:
        print(f"Não foi possível ler o arquivo: {e}")
        return None


def tratar_dados(df):
    print("Limpando dados com o pandas")

    colunas_interesse = [
        'co_anomes',
        'co_ibge',
        'no_municipio',
        'sg_uf',
        'no_regiao_brasil',
        'vl_indicador_calculado_mun'
    ]

    colunas_ausentes = [c for c in colunas_interesse if c not in df.columns]
    if colunas_ausentes:
        print(f"Colunas não encontradas no CSV: {colunas_ausentes}")
        return None

    df_limpo = df[colunas_interesse].copy()

    print(f"Registros antes da limpeza: {len(df_limpo)}")

    df_limpo = df_limpo.dropna(subset=['co_ibge'])

    df_limpo['vl_indicador_calculado_mun'] = (
        df_limpo['vl_indicador_calculado_mun'].fillna(0)
    )

    df_limpo['no_municipio'] = df_limpo['no_municipio'].str.strip()
    df_limpo['sg_uf'] = df_limpo['sg_uf'].str.strip()
    df_limpo['no_regiao_brasil'] = df_limpo['no_regiao_brasil'].str.strip()

    df_limpo['co_anomes'] = df_limpo['co_anomes'].astype(int)
    df_limpo['co_ibge'] = df_limpo['co_ibge'].astype(int)
    df_limpo['vl_indicador_calculado_mun'] = (
        df_limpo['vl_indicador_calculado_mun'].astype(float)
    )

    print(f"Registros após a limpeza:  {len(df_limpo)}")
    print("\nResumo do indicador de mamografia:")
    print(f"  Média:   {df_limpo['vl_indicador_calculado_mun'].mean():.2f}")
    print(f"  Mínimo:  {df_limpo['vl_indicador_calculado_mun'].min():.2f}")
    print(f"  Máximo:  {df_limpo['vl_indicador_calculado_mun'].max():.2f}")
    print()

    return df_limpo


def conectar_banco():
    print("Conectando ao banco de dados MySQL")

    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'projeto_saude'
    }

    try:
        conexao = mysql.connector.connect(**config)

        if conexao.is_connected():
            print(f"Conectado ao MySQl")
            print(f"     Banco de dados: {config['database']}\n")
            return conexao

    except Error as e:
        print(f"Falha ao conectar ao MySQL: {e}")
        return None


def criar_tabela(conexao):
    cursor = conexao.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS indicadores_mamografia (
        co_anomes       INT          NOT NULL,
        co_ibge         INT          NOT NULL,
        no_municipio    VARCHAR(100) NOT NULL,
        sg_uf           CHAR(2)      NOT NULL,
        no_regiao       VARCHAR(50)  NOT NULL,
        valor_indicador FLOAT        NOT NULL DEFAULT 0,
        PRIMARY KEY (co_anomes, co_ibge)
    );
    """

    try:
        cursor.execute(query)
        conexao.commit()
        print("Tabela 'indicadores_mamografia' criada.\n")
    except Error as e:
        print(f"Falha ao criar tabela: {e}")
    finally:
        cursor.close()


def inserir_dados(conexao, df):
    print("inserindo dados no banco de dados")

    cursor = conexao.cursor()

    query = """
    INSERT INTO indicadores_mamografia
        (co_anomes, co_ibge, no_municipio, sg_uf, no_regiao, valor_indicador)
    VALUES
        (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        no_municipio    = VALUES(no_municipio),
        sg_uf           = VALUES(sg_uf),
        no_regiao       = VALUES(no_regiao),
        valor_indicador = VALUES(valor_indicador);
    """

    inseridos = 0

    try:
        for _, row in df.iterrows():
            valores = (
                int(row['co_anomes']),
                int(row['co_ibge']),
                str(row['no_municipio']),
                str(row['sg_uf']),
                str(row['no_regiao_brasil']),
                float(row['vl_indicador_calculado_mun'])
            )
            cursor.execute(query, valores)
            inseridos += 1

            if inseridos % 1000 == 0:
                print(f"  Progresso: {inseridos}/{len(df)} registros processados")

        conexao.commit()
        print(f"\n{inseridos} registros inseridos\n")

    except Error as e:
        print(f"\nErro na inserção: {e}")
        print(f"      rollback")
        conexao.rollback()

    finally:
        cursor.close()


def consultar_dados_banco(conexao):
    print("Consultando dados do banco para analise")

    query = "SELECT * FROM indicadores_mamografia;"

    try:
        df_banco = pd.read_sql(query, conexao)
        print(f"{len(df_banco)} registros recuperados do banco.\n")
        return df_banco
    except Error as e:
        print(f"Erro ao consultar banco: {e}")
        return None


def gerar_graficos(df):
    print("Gerando gráficos de análise")

    cores = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974']

    plt.figure(figsize=(10, 6))

    analise_regiao = (
        df.groupby('no_regiao_brasil')['vl_indicador_calculado_mun']
        .sum()
        .sort_values(ascending=False)
    )

    analise_regiao_milhoes = analise_regiao / 1_000_000
    analise_regiao_milhoes.plot(kind='bar', color=cores[:len(analise_regiao)], edgecolor='black')

    plt.title('Cobertura de Mamografia por Região do Brasil\n(Soma Acumulada dos Indicadores)', fontsize=13)
    plt.xlabel('Região', fontsize=11)
    plt.ylabel('Soma dos Indicadores (milhões)', fontsize=11)
    plt.xticks(rotation=30, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('grafico_regioes.png', dpi=100)
    plt.close()
    print("Gráfico 1 salvo: 'grafico_regioes.png'")

    plt.figure(figsize=(12, 6))

    evolucao = (
        df.groupby('co_anomes')['vl_indicador_calculado_mun']
        .sum()
    )

    evolucao_milhoes = evolucao / 1_000_000

    rotulos = [
        f"{str(x)[4:6]}/{str(x)[:4]}" for x in evolucao.index
    ]

    plt.plot(range(len(evolucao_milhoes)), evolucao_milhoes.values, marker='o', color='green', linewidth=2, markersize=5)
    plt.xticks(ticks=range(len(evolucao_milhoes)), labels=rotulos, rotation=45, ha='right')

    plt.title('Evolução da Cobertura de Mamografia no Brasil\n(Total por Período)', fontsize=13)
    plt.xlabel('Período (Mês/Ano)', fontsize=11)
    plt.ylabel('Soma dos Indicadores (milhões)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('grafico_evolucao.png', dpi=100)
    plt.close()
    print("Gráfico 2 salvo: 'grafico_evolucao.png'")

    plt.figure(figsize=(8, 8))

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        analise_regiao.values,
        labels=None,
        autopct='%1.1f%%',
        colors=cores[:len(analise_regiao)],
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )

    ax.legend(
        wedges,
        analise_regiao.index,
        title="Regiões",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    plt.title('Distribuição Percentual de Mamografias\npor Região do Brasil', fontsize=13)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('grafico_pizza.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("Gráfico 3 salvo: 'grafico_pizza.png'\n")


def exibir_estatisticas(df):
    print("RESUMO ESTATÍSTICO DOS DADOS")

    resumo = (
        df.groupby('no_regiao_brasil')['vl_indicador_calculado_mun']
        .agg(
            Total='sum',
            Media='mean',
            Minimo='min',
            Maximo='max',
            Municipios='count'
        )
        .round(2)
        .sort_values('Total', ascending=False)
    )

    print(resumo.to_string())
    print()


def explicar_automacao():
    print("cron:")
    print("  crontab -e no  terminal")
    print("  0 8 * * * /usr/bin/python3 /home/thiagoceron/Documentos/CienciaDados/TrabalhoIII/trabalho.py")

if __name__ == "__main__":

    print(" Mamografia TrabalhoIII")

    ARQUIVO_CSV = "mamografia.csv"

    dados_brutos = coletar_dados(ARQUIVO_CSV)

    if dados_brutos is None:
        print("Erro dados csv")
        exit(1)

    dados_processados = tratar_dados(dados_brutos)

    if dados_processados is None:
        print("Erro no processamento dos dados")
        exit(1)

    exibir_estatisticas(dados_processados)

    conexao = conectar_banco()

    if conexao and conexao.is_connected():
        criar_tabela(conexao)
        inserir_dados(conexao, dados_processados)
        conexao.close()
        print("Conexão com o banco encerrada\n")
    else:
        print("Graficos gerados pelo csv\n")

    gerar_graficos(dados_processados)

    explicar_automacao()

    print("\nArquivos gerados:")
    print("  - grafico_regioes.png  (barras por região)")
    print("  - grafico_evolucao.png (linha temporal)")
    print("  - grafico_pizza.png    (distribuição por região)")
    print()