import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    arquivos = [
        "matriz_de_dados_credito_rural_2015-2016.parquet",
        "matriz_de_dados_credito_rural_2016-2017.parquet",
        "matriz_de_dados_credito_rural_2017-2018.parquet",
        "matriz_de_dados_credito_rural_2018-2019.parquet",
        "matriz_de_dados_credito_rural_2019-2020.parquet",
        "matriz_de_dados_credito_rural_2020-2021.parquet",
        "matriz_de_dados_credito_rural_2021-2022.parquet",
        "matriz_de_dados_credito_rural_2022-2023.parquet",
        "matriz_de_dados_credito_rural_2023-2024.parquet",
        "matriz_de_dados_credito_rural_2024-2025.parquet",
        "matriz_de_dados_credito_rural_2025-2026.parquet"
    ]
    
    lista_dfs = []
    for arq in arquivos:
        if os.path.exists(arq):
            try:
                df_temp = pd.read_parquet(arq)
                lista_dfs.append(df_temp)
            except Exception as e:
                st.warning(f"Aviso: Não foi possível ler {arq}. Erro: {e}")

    if not lista_dfs:
        st.error("Nenhum dos arquivos especificados foi encontrado.")
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira', 'Ano_Safra': 'Ano Safra'})
    df[['UF', 'Instituição Financeira', 'Ano Safra']] = df[['UF', 'Instituição Financeira', 'Ano Safra']].astype('category')
    df[['Mes_Emissao', 'Ano_Emissao']] = df[['Mes_Emissao', 'Ano_Emissao']].astype(int)
    return df

df = load_data()
st.write(df.head())
