import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da página sempre no topo
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    lista_dfs = []
    # Carregamento seguro dos arquivos
    for ano in range(2015, 2026):
        arquivo = f"matriz_de_dados_credito_rural_{ano}-{ano+1}.parquet"
        if os.path.exists(arquivo):
            try:
                temp_df = pd.read_parquet(arquivo)
                lista_dfs.append(temp_df)
            except Exception:
                continue
    
    if not lista_dfs:
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.rename(columns={'Classificacao_IF': 'Instituição Financeira', 'Ano_Safra': 'Ano Safra'})
    df[['UF', 'Instituição Financeira', 'Ano Safra']] = df[['UF', 'Instituição Financeira', 'Ano Safra']].astype('category')
    return df

df = load_data()

if df.empty:
    st.warning("Aguardando carregamento de dados...")
    st.stop()

# --- Sidebar e Filtros ---
with st.sidebar:
    st.header("🔍 Filtros")
    tema = st.radio("Tema Visual", ["Claro", "Dark"], key="radio_tema")
    inst_sel = st.multiselect("Instituições", sorted(df['Instituição Financeira'].unique()))
    anos_safra = sorted(df['Ano Safra'].unique().tolist())
    safra_sel = st.multiselect("Safras", anos_safra, default=[anos_safra[-1]])
    
    st.subheader("📅 Período")
    ordem_safra = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    nomes_meses = {7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez", 1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun"}
    
    mes_inicio_nome, mes_fim_nome = st.select_slider(
        "Intervalo", options=[nomes_meses[m] for m in ordem_safra], value=("Jul", "Jun")
    )

# --- CSS Estabilizado (Evita removeChild Error) ---
bg_color = "#0E1117" if tema == "Dark" else "#FFFFFF"
text_color = "#FFFFFF" if tema == "Dark" else "#000000"
plotly_template = "plotly_dark" if tema == "Dark" else "plotly_white"

# O segredo é manter o ID do style fixo para o React não tentar deletar o nó
st.markdown(f"""
    <style id="main_style">
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        h1, h2, h3, h4, h5, p, span, label {{ color: {text_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- Processamento ---
mes_inicio = [k for k, v in nomes_meses.items() if v == mes_inicio_nome][0]
mes_fim = [k for k, v in nomes_meses.items() if v == mes_fim_nome][0]
idx_i, idx_f = ordem_safra.index(mes_inicio), ordem_safra.index(mes_fim)
meses_validos = ordem_safra[idx_i : idx_f + 1] if idx_i <= idx_f else ordem_safra[idx_i:] + ordem_safra[:idx_f + 1]

df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel: df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel: df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- Interface ---
st.title("🌱 Intelligence Crédito Rural")

if not df_f.empty:
    # Gráfico com chave fixa
    st.subheader("📈 Evolução Mensal")
    valores_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
    evol_data = df_f.groupby(['Instituição Financeira', 'Ano Safra', 'Mes_Emissao'], observed=True)[valores_cols].sum().sum(axis=1).reset_index(name='Total')
    evol_data['Total_BI'] = evol_data['Total'] / 1e9

    fig = px.line(evol_data, x='Mes_Emissao', y='Total_BI', color='Instituição Financeira', 
                 facet_col='Ano Safra', category_orders={"Mes_Emissao": ordem_safra},
                 template=plotly_template)
    st.plotly_chart(fig, use_container_width=True, key="grafico_principal")

    # Tabelas dentro de Containers Estáticos
    st.subheader("📋 Relatório por Safra")
    
    rel_bruto = df_f.groupby(['Ano Safra', 'Instituição Financeira'], observed=True)[valores_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    rel_bi = rel_bruto / 1e9
    df_final = rel_bi.reset_index()

    for safra in sorted(df_final['Ano Safra'].unique(), reverse=True):
        # O container garante que o Streamlit reserve um espaço fixo no DOM
        with st.container():
            st.write(f"### Safra {safra}")
            df_safra = df_final[df_final['Ano Safra'] == safra]
            
            st.dataframe(
                df_safra, 
                use_container_width=True, 
                hide_index=True,
                key=f"data_table_{safra}" # A chave deve ser única por safra
            )
else:
    st.info("Nenhum dado encontrado para os filtros atuais.")