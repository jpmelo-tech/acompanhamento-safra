import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Teste Arquivos Parquet", page_icon="📂", layout="wide")

anos = [
    "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
    "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
]

for ano in anos:
    arq = f"matriz_de_dados_credito_rural_{ano}.parquet"
    st.markdown(f"### Arquivo: {arq}")
    if os.path.exists(arq):
        try:
            df_temp = pd.read_parquet(arq)
            st.success(f"✅ Lido com sucesso! {len(df_temp)} linhas, {len(df_temp.columns)} colunas.")
            st.write(df_temp.head())
        except Exception as e:
            st.error(f"❌ Erro ao ler {arq}: {e}")
    else:
        st.warning(f"⚠️ Arquivo {arq} não encontrado.")
