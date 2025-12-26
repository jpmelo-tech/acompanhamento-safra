import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Tipagem Segura", layout="wide")

base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = ["2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
        "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"]
dfs = [pd.read_parquet(base_url + f"matriz_de_dados_credito_rural_{ano}.parquet") for ano in anos]
df = pd.concat(dfs, ignore_index=True)

# Renomeação
df = df.rename(columns={'Classificacao_IF':'Instituição Financeira','Ano_Safra':'Ano Safra'})

# Tipagem segura
if 'Mes_Emissao' in df.columns:
    df['Mes_Emissao'] = pd.to_numeric(df['Mes_Emissao'], errors="coerce").astype("Int64")
if 'Ano_Emissao' in df.columns:
    df['Ano_Emissao'] = pd.to_numeric(df['Ano_Emissao'], errors="coerce").astype("Int64")

# Para categorias, apenas converter para string (evita bug do frontend)
for col in ['UF','Instituição Financeira','Ano Safra']:
    if col in df.columns:
        df[col] = df[col].astype(str)

st.success("Tipagem aplicada com segurança.")
st.write(df.dtypes)
st.write(df.head(20))
