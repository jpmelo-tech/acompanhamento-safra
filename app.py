import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da página (DEVE ser o primeiro comando)
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    lista_dfs = []
    for ano in range(2015, 2026):
        arquivo = f"matriz_de_dados_credito_rural_{ano}-{ano+1}.parquet"
        if os.path.exists(arquivo):
            try:
                temp_df = pd.read_parquet(arquivo)
                lista_dfs.append(temp_df)
            except:
                continue
    
    if not lista_dfs:
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira', 'Ano_Safra': 'Ano Safra'})
    
    # Conversão de tipos para estabilidade
    df['Ano Safra'] = df['Ano Safra'].astype(str)
    df['Instituição Financeira'] = df['Instituição Financeira'].astype(str)
    return df

df = load_data()

if df.empty:
    st.error("Dados não encontrados.")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.header("🔍 Filtros")
    tema = st.radio("Tema Visual", ["Claro", "Dark"], key="main_theme_selector")
    
    instituicoes = sorted(df['Instituição Financeira'].unique())
    inst_sel = st.multiselect("Instituições", instituicoes, key="inst_filter")
    
    anos_safra = sorted(df['Ano Safra'].unique().tolist())
    safra_sel = st.multiselect("Safras", anos_safra, default=[anos_safra[-1]], key="safra_filter")

# --- CSS Estabilizado (O segredo para evitar o erro de Node) ---
bg_color = "#0E1117" if tema == "Dark" else "#FFFFFF"
text_color = "#FFFFFF" if tema == "Dark" else "#000000"
plotly_template = "plotly_dark" if tema == "Dark" else "plotly_white"

# Injetamos o estilo com uma KEY fixa para o Streamlit não recriar o nó do DOM
st.markdown(f"""
    <style id="custom_styles">
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        h1, h2, h3, h4, h5, p, span, label {{ color: {text_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- Lógica de Datas ---
ordem_safra = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
nomes_meses = {7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez", 1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun"}

with st.sidebar:
    st.subheader("📅 Período")
    mes_inicio_nome, mes_fim_nome = st.select_slider(
        "Intervalo", options=[nomes_meses[m] for m in ordem_safra], value=("Jul", "Jun"), key="period_slider"
    )

mes_inicio = [k for k, v in nomes_meses.items() if v == mes_inicio_nome][0]
mes_fim = [k for k, v in nomes_meses.items() if v == mes_fim_nome][0]
idx_i, idx_f = ordem_safra.index(mes_inicio), ordem_safra.index(mes_fim)
meses_validos = ordem_safra[idx_i : idx_f + 1] if idx_i <= idx_f else ordem_safra[idx_i:] + ordem_safra[:idx_f + 1]

# --- Filtragem ---
df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel: df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel: df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- Renderização Principal ---
st.title("🌱 Intelligence Crédito Rural")
st.info(f"Período: {mes_inicio_nome} até {mes_fim_nome}")

if not df_f.empty:
    # Gráfico com KEY fixa
    st.subheader("📈 Evolução Mensal")
    v_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
    evol = df_f.groupby(['Instituição Financeira', 'Ano Safra', 'Mes_Emissao'])[v_cols].sum().sum(axis=1).reset_index(name='Total')
    evol['Total_BI'] = evol['Total'] / 1e9

    fig = px.line(evol, x='Mes_Emissao', y='Total_BI', color='Instituição Financeira', 
                 facet_col='Ano Safra', markers=True, template=plotly_template,
                 category_orders={"Mes_Emissao": ordem_safra})
    st.plotly_chart(fig, use_container_width=True, key="main_chart")

    # Relatórios em containers isolados
    st.subheader("📋 Relatório por Safra")
    
    rel_bruto = df_f.groupby(['Ano Safra', 'Instituição Financeira'])[v_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    df_rel = (rel_bruto / 1e9).reset_index()

    for safra in sorted(df_rel['Ano Safra'].unique(), reverse=True):
        # Usar container isola o erro de 'removeChild' dentro de cada bloco
        with st.container():
            st.markdown(f"#### Safra {safra}")
            df_temp = df_rel[df_rel['Ano Safra'] == safra].sort_values('Total', ascending=False)
            st.dataframe(
                df_temp, 
                use_container_width=True, 
                hide_index=True,
                key=f"table_safra_{safra}" # Key única por safra
            )
            st.divider()
else:
    st.warning("Sem dados para os filtros selecionados.")