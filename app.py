import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
    arquivos = [
        f"matriz_de_dados_credito_rural_{ano}.parquet"
        for ano in [
            "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
            "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
        ]
    ]
    lista_dfs = []
    for arq in arquivos:
        url = base_url + arq
        try:
            lista_dfs.append(pd.read_parquet(url))
        except Exception as e:
            # Apenas log, sem st.warning
            print(f"Erro ao ler {arq}: {e}")
    if not lista_dfs:
        return pd.DataFrame()
    df = pd.concat(lista_dfs, ignore_index=True)
    if 'Classificacao_IF' in df.columns:
        df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira'})
    if 'Ano_Safra' in df.columns:
        df = df.rename(columns={'Ano_Safra': 'Ano Safra'})
    return df

df = load_data()

if df.empty:
    st.error("Nenhum dado foi carregado.")
    st.stop()

st.success(f"{len(df)} linhas carregadas.")

# Teste simples: mostrar apenas preview
st.write(df.head())