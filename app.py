import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Teste Parquet", page_icon="🌱", layout="wide")

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
            lista_dfs.append(pd.read_parquet(arq))
        except Exception as e:
            st.write(f"Erro ao ler {arq}: {e}")

if lista_dfs:
    df = pd.concat(lista_dfs, ignore_index=True)
    st.success("Arquivos lidos com sucesso!")
    st.write(df.head())
else:
    st.error("Nenhum arquivo foi encontrado.")

