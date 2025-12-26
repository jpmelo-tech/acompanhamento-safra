import streamlit as st
import pandas as pd

st.set_page_config(page_title="Concatenação segura", page_icon="🧩", layout="wide")
st.title("🧩 Teste de concatenação dos arquivos Parquet")

base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = [
    "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
    "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
]
arquivos = [f"matriz_de_dados_credito_rural_{ano}.parquet" for ano in anos]

dfs = []
for arq in arquivos:
    url = base_url + arq
    dfs.append(pd.read_parquet(url))

df = pd.concat(dfs, ignore_index=True)

st.success(f"Concatenação concluída: {len(df)} linhas, {len(df.columns)} colunas, {len(dfs)} arquivos.")
st.subheader("Preview")
st.dataframe(df.head(50), use_container_width=True, key="preview_concat")
