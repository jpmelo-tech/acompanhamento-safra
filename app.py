import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Filtros", page_icon="🧩", layout="wide")
st.title("🧩 Teste com filtros básicos (sem tipagem)")

# --- Leitura e concatenação ---
base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = [
    "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
    "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
]
arquivos = [f"matriz_de_dados_credito_rural_{ano}.parquet" for ano in anos]

dfs = [pd.read_parquet(base_url + arq) for arq in arquivos]
df = pd.concat(dfs, ignore_index=True)

# --- Renomeação simples ---
df = df.rename(columns={'Classificacao_IF':'Instituição Financeira','Ano_Safra':'Ano Safra'})

# --- Sidebar com filtros ---
st.sidebar.header("🔍 Filtros")
anos_safra = sorted(df['Ano Safra'].unique().tolist())
inst_sel = st.sidebar.multiselect("Instituições", sorted(df['Instituição Financeira'].unique()))
safra_sel = st.sidebar.multiselect("Safras", anos_safra, default=[anos_safra[-1]])

# --- Aplicação dos filtros ---
df_f = df.copy()
if safra_sel:
    df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel:
    df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- Resultado ---
st.success(f"DataFrame filtrado: {len(df_f)} linhas, {len(df_f.columns)} colunas")
st.subheader("Preview filtrado")
st.dataframe(df_f.head(50), use_container_width=True, key="preview_filtros")
