import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("matriz_de_dados_credito_rural.csv")
    df = df[df['Ano_Safra'] >= '2017/2018'].copy()
    df[['UF', 'Classificacao_IF']] = df[['UF', 'Classificacao_IF']].astype('category')
    df[['Mes_Emissao', 'Ano_Emissao']] = df[['Mes_Emissao', 'Ano_Emissao']].astype(int)
    return df

df = load_data()
valores_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
anos_safra = sorted(df['Ano_Safra'].unique().tolist())

# --- Sidebar ---
st.sidebar.header("🔍 Filtros Estratégicos")
tema = st.sidebar.radio("Tema Visual", ["Claro", "Dark"])
inst_sel = st.sidebar.multiselect("Instituições", sorted(df['Classificacao_IF'].unique()))
safra_sel = st.sidebar.multiselect("Safras", anos_safra, default=[anos_safra[-1]])

# --- CSS Dinâmico para o Tema ---
if tema == "Dark":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    card_color = "#262730"
    separator = "white"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    card_color = "#F0F2F6"
    separator = "black"
    plotly_template = "plotly_white"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    [data-testid="stSidebar"] {{ background-color: {card_color}; }}
    h1, h2, h3, p {{ color: {text_color} !important; }}
    /* Ajuste para as métricas */
    [data-testid="stMetricValue"] {{ color: #1E90FF !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- Lógica de Meses Espelhados ---
ordem_safra = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
nomes_meses = {7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez", 1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun"}

st.sidebar.subheader("📅 Período da Safra")
mes_inicio_nome, mes_fim_nome = st.sidebar.select_slider(
    "Intervalo de meses",
    options=[nomes_meses[m] for m in ordem_safra],
    value=("Jul", "Jun")
)

mes_inicio = [k for k, v in nomes_meses.items() if v == mes_inicio_nome][0]
mes_fim = [k for k, v in nomes_meses.items() if v == mes_fim_nome][0]

idx_i, idx_f = ordem_safra.index(mes_inicio), ordem_safra.index(mes_fim)
meses_validos = ordem_safra[idx_i : idx_f + 1] if idx_i <= idx_f else ordem_safra[idx_i:] + ordem_safra[:idx_f + 1]

# --- Filtragem ---
df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel: df_f = df_f[df_f['Ano_Safra'].isin(safra_sel)]
if inst_sel: df_f = df_f[df_f['Classificacao_IF'].isin(inst_sel)]

# --- Interface ---
st.title("🌱 Intelligence Crédito Rural")

if not df_f.empty:
    # 1. Gráfico de Evolução
    st.subheader("📈 Evolução Mensal")
    evol_data = df_f.groupby(['Classificacao_IF', 'Ano_Safra', 'Mes_Emissao'], observed=True)[valores_cols].sum().sum(axis=1).reset_index(name='Total')
    evol_data['Total_BI'] = evol_data['Total'] / 1e9

    fig_line = px.line(evol_data, x='Mes_Emissao', y='Total_BI', color='Classificacao_IF', 
                       facet_col='Ano_Safra', markers=True,
                       category_orders={"Mes_Emissao": ordem_safra},
                       labels={"Total_BI": "Volume (Bi R$)"},
                       template=plotly_template)
    st.plotly_chart(fig_line, use_container_width=True)

    # 2. Relatório Detalhado
    st.subheader("📋 Relatório de Share por Finalidade")
    
    rel_bruto = df_f.groupby(['Ano_Safra', 'Classificacao_IF'], observed=True)[valores_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    rel_pct = (rel_bruto.div(rel_bruto.groupby(level=0).sum(), level=0) * 100)
    rel_pct.columns = [c + " (%)" for c in rel_pct.columns]
    rel_bi = rel_bruto / 1e9

    df_final = pd.concat([rel_bi, rel_pct], axis=1).reset_index()

    for safra in sorted(df_final['Ano_Safra'].unique(), reverse=True):
        st.markdown(f"### 🗓️ Safra {safra}")
        df_safra = df_final[df_final['Ano_Safra'] == safra].sort_values(by='Total', ascending=False)

        col_configs = {
            "Ano_Safra": None,
            "Classificacao_IF": st.column_config.TextColumn("Instituição"),
            "Total": st.column_config.NumberColumn("Total", format="R$ %.2f BI"),
            "Total (%)": st.column_config.ProgressColumn("Market Share", format="%.2f%%", min_value=0, max_value=100)
        }
        for col in valores_cols:
            nome = col.replace("Valor_", "")
            col_configs[col] = st.column_config.NumberColumn(nome, format="R$ %.2f BI")
            col_configs[col + " (%)"] = st.column_config.NumberColumn(nome + " %", format="%.2f%%")

        st.dataframe(df_safra, column_config=col_configs, use_container_width=True, hide_index=True)
        st.markdown(f"<hr style='border: 1px solid {separator};'>", unsafe_allow_html=True)

else:
    st.warning("Sem dados para o intervalo selecionado.")