import streamlit as st
import pandas as pd
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
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
                # Apenas registra o erro, sem renderizar nada
                print(f"Erro ao ler {arq}: {e}")

    if not lista_dfs:
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira', 'Ano_Safra': 'Ano Safra'})
    
    # Tipagem
    for col in ['UF', 'Instituição Financeira', 'Ano Safra']:
        if col in df.columns:
            df[col] = df[col].astype('category')
    for col in ['Mes_Emissao', 'Ano_Emissao']:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    return df

# --- Uso ---
df = load_data()

if df.empty:
    st.error("Nenhum arquivo foi encontrado ou pôde ser lido.")
    st.stop()

st.success("Dados carregados com sucesso!")
st.write(df.head())
