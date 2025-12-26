import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste", layout="wide")

df = pd.read_parquet("https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/matriz_de_dados_credito_rural_2015-2016.parquet")
st.write(df.head())
