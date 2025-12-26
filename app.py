import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste", layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/matriz_de_dados_credito_rural_2015-2016.parquet"
    return pd.read_parquet(url)

df = load_data()
st.write(df.head())