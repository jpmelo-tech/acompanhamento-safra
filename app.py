import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Tipagem", page_icon="🧩", layout="wide")
st.title("🧩 Teste de Tipagem e Renomeação")

# --- Leitura e concatenação ---
base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = [
    "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
    "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
]
arquivos = [f"matriz_de_dados_credito_rural_{ano}.parquet" for ano in anos]

dfs = [pd.read_parquet(base_url + arq) for arq in arquivos]
df = pd.concat(dfs, ignore_index=True)

# --- Renomeação ---
if 'Classificacao_IF' in df.columns:
    df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira'})
if 'Ano_Safra' in df.columns:
    df = df.rename(columns={'Ano_Safra': 'Ano Safra'})

# --- Tipagem ---
for col in ['UF', 'Instituição Financeira', 'Ano Safra']:
    if col in df.columns:
        df[col] = df[col].astype('category')

for col in ['Mes_Emissao', 'Ano_Emissao']:
    if col in df.columns:
        df[col] = df[col].astype(int)

# --- Resultado ---
st.success(f"DataFrame final: {len(df)} linhas, {len(df.columns)} colunas")
st.subheader("Preview pós-tipagem")
st.dataframe(df.head(50), use_container_width=True, key="preview_tipagem")
