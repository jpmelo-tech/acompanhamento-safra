import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

# --- Leitura direta dos arquivos ---
arquivos = [
    f"matriz_de_dados_credito_rural_{ano}.parquet"
    for ano in [
        "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
        "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
    ]
]

lista_dfs = []
for arq in arquivos:
    if os.path.exists(arq):
        try:
            df_temp = pd.read_parquet(arq)
            lista_dfs.append(df_temp)
        except Exception as e:
            st.warning(f"Erro ao ler {arq}: {e}")
    else:
        st.warning(f"Arquivo não encontrado: {arq}")

if not lista_dfs:
    st.error("Nenhum arquivo foi carregado.")
    st.stop()

df = pd.concat(lista_dfs, ignore_index=True)

# --- Visualização simples para validar ---
st.success(f"{len(df)} linhas carregadas de {len(lista_dfs)} arquivos.")
st.write(df.head())
