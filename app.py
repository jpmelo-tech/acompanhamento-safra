import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

# --- Carregamento dos dados ---
base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = ["2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
        "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"]
arquivos = [f"matriz_de_dados_credito_rural_{ano}.parquet" for ano in anos]
dfs = [pd.read_parquet(base_url + arq) for arq in arquivos]
df = pd.concat(dfs, ignore_index=True)

df = df.rename(columns={'Classificacao_IF':'Instituição Financeira','Ano_Safra':'Ano Safra'})

# --- Sidebar ---
st.sidebar.header("🔍 Filtros")
anos_safra = sorted(df['Ano Safra'].unique())
safra_sel = st.sidebar.multiselect("Safra", anos_safra, default=anos_safra)
inst_sel = st.sidebar.multiselect("Instituições", sorted(df['Instituição Financeira'].unique()))

# --- Filtragem ---
df_f = df[(df['Ano Safra'].isin(safra_sel)) & (df['Instituição Financeira'].isin(inst_sel))]

# --- KPIs ---
st.title("🌱 Inteligência do Crédito Rural")
st.subheader("Métricas gerais (em bilhões R$)")
if not df_f.empty:
    total = df_f[['Valor_Custeio','Valor_Investimento','Valor_Comercializacao','Valor_Industrializacao']].sum().sum() / 1e9
    media = df_f[['Valor_Custeio','Valor_Investimento','Valor_Comercializacao','Valor_Industrializacao']].mean().mean() / 1e9
    registros = df_f.shape[0]
    inst_mais = df_f['Instituição Financeira'].mode()[0]
else:
    total, media, registros, inst_mais = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", f"R$ {total:,.2f} BI")
col2.metric("Média", f"R$ {media:,.2f} BI")
col3.metric("Registros", f"{registros:,}")
col4.metric("Instituição mais frequente", inst_mais)

st.markdown("---")

# --- Gráficos ---
st.subheader("📈 Evolução Mensal")
if not df_f.empty:
    valores_cols = ['Valor_Custeio','Valor_Investimento','Valor_Comercializacao','Valor_Industrializacao']
    evol = df_f.groupby(['Ano Safra','Mes_Emissao'])[valores_cols].sum().sum(axis=1).reset_index(name='Total')
    evol['Total_BI'] = evol['Total']/1e9
    fig = px.line(evol, x='Mes_Emissao', y='Total_BI', color='Ano Safra', markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir no gráfico.")

# --- Tabela final ---
st.subheader("Dados Detalhados")
st.dataframe(df_f)
