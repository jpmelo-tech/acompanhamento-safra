import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Teste", page_icon="🌱", layout="wide")
st.title("🌱 Teste com filtros e gráfico (sem st.dataframe)")

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

# --- Resultado filtrado ---
st.success(f"DataFrame filtrado: {len(df_f)} linhas, {len(df_f.columns)} colunas")
st.subheader("Preview filtrado (via st.write)")
st.write(df_f.head(20))   # usamos st.write em vez de st.dataframe

# --- Gráfico simples ---
if not df_f.empty:
    st.subheader("📈 Evolução Mensal (teste)")
    valores_cols = ['Valor_Custeio','Valor_Investimento','Valor_Comercializacao','Valor_Industrializacao']
    evol_data = df_f.groupby(['Ano Safra','Mes_Emissao'])[valores_cols].sum().sum(axis=1).reset_index(name='Total')
    evol_data['Total_BI'] = evol_data['Total'] / 1e9

    fig = px.line(evol_data, x='Mes_Emissao', y='Total_BI', color='Ano Safra', markers=True)
    st.plotly_chart(fig, use_container_width=True, key="grafico_teste")
else:
    st.warning("Nenhum dado encontrado para os filtros atuais.")
