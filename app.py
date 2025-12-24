import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    lista_dfs = []
    for ano in range(2015, 2026):
        prox_ano = ano + 1
        arquivo = f"matriz_de_dados_credito_rural_{ano}-{prox_ano}.parquet"
        
        if os.path.exists(arquivo):
            try:
                temp_df = pd.read_parquet(arquivo)
                lista_dfs.append(temp_df)
            except Exception as e:
                st.error(f"Erro ao carregar {arquivo}: {e}")
    
    if not lista_dfs:
        st.error("Nenhum arquivo Parquet encontrado. Certifique-se de que eles estão na raiz do repositório.")
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    
    # Renomeação de Colunas
    df = df.rename(columns={
        'Classificacao_IF': 'Instituição Financeira',
        'Ano_Safra': 'Ano Safra'
    })
    
    # Otimização de tipos
    df[['UF', 'Instituição Financeira', 'Ano Safra']] = df[['UF', 'Instituição Financeira', 'Ano Safra']].astype('category')
    df[['Mes_Emissao', 'Ano_Emissao']] = df[['Mes_Emissao', 'Ano_Emissao']].astype(int)
    
    return df

df = load_data()

if df.empty:
    st.stop()

valores_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
anos_safra = sorted(df['Ano Safra'].unique().tolist())

# --- Sidebar ---
st.sidebar.header("🔍 Filtros Estratégicos")
tema = st.sidebar.radio("Tema Visual", ["Claro", "Dark"])
inst_sel = st.sidebar.multiselect("Instituições", sorted(df['Instituição Financeira'].unique()))
safra_sel = st.sidebar.multiselect("Safras", anos_safra, default=[anos_safra[-1]])

# --- CSS Dinâmico Estabilizado ---
if tema == "Dark":
    bg_color, text_color, card_color = "#0E1117", "#FFFFFF", "#262730"
    plotly_template = "plotly_dark"
else:
    bg_color, text_color, card_color = "#FFFFFF", "#000000", "#F0F2F6"
    plotly_template = "plotly_white"

# Removido seletor de centralização agressiva que causava erro de 'removeChild'
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    [data-testid="stSidebar"] {{ background-color: {card_color}; }}
    h1, h2, h3, h5, p {{ color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- Cabeçalho Principal ---
st.title("🌱 Intelligence Crédito Rural")
st.markdown("##### Fonte: Matriz de Dados do Crédito Rural do Banco Central do Brasil")

# --- Lógica de Meses ---
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

periodo_texto = f"Período selecionado: **{mes_inicio_nome}** até **{mes_fim_nome}**"
st.info(f"📅 {periodo_texto}")
st.divider() # Usando o componente nativo em vez de markdown horizontal rule

# --- Filtragem ---
df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel: df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel: df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- Visualizações ---
if not df_f.empty:
    # 1. Gráfico de Evolução
    st.subheader("📈 Evolução Mensal")
    evol_data = df_f.groupby(['Instituição Financeira', 'Ano Safra', 'Mes_Emissao'], observed=True)[valores_cols].sum().sum(axis=1).reset_index(name='Total')
    evol_data['Total_BI'] = evol_data['Total'] / 1e9

    fig_line = px.line(evol_data, x='Mes_Emissao', y='Total_BI', color='Instituição Financeira', 
                       facet_col='Ano Safra', markers=True,
                       category_orders={"Mes_Emissao": ordem_safra},
                       labels={"Total_BI": "Volume (Bi R$)", "Mes_Emissao": "Mês", "Instituição Financeira": "Instituição"},
                       template=plotly_template)
    st.plotly_chart(fig_line, use_container_width=True, key="grafico_evolucao")

    # 2. Relatório Completo
    st.subheader("📋 Relatório Completo por Finalidade")
    
    rel_bruto = df_f.groupby(['Ano Safra', 'Instituição Financeira'], observed=True)[valores_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    rel_pct = (rel_bruto.div(rel_bruto.groupby(level=0).sum(), level=0) * 100)
    rel_pct.columns = [c + " (%)" for c in rel_pct.columns]
    rel_bi = rel_bruto / 1e9

    df_final = pd.concat([rel_bi, rel_pct], axis=1).reset_index()

    # Loop com chaves únicas para evitar o erro NotFoundError de Node
    for i, safra in enumerate(sorted(df_final['Ano Safra'].unique(), reverse=True)):
        st.markdown(f"### 🗓️ Safra {safra}")
        df_safra = df_final[df_final['Ano Safra'] == safra].sort_values(by='Total', ascending=False)

        col_configs = {
            "Ano Safra": None,
            "Instituição Financeira": st.column_config.TextColumn("Instituição Financeira"),
            "Total": st.column_config.NumberColumn("Total", format="R$ %.2f BI"),
            "Total (%)": st.column_config.ProgressColumn("Market Share", format="%.2f%%", min_value=0, max_value=100)
        }
        
        for col in valores_cols:
            nome = col.replace("Valor_", "")
            col_configs[col] = st.column_config.NumberColumn(nome, format="R$ %.2f BI")
            col_configs[col + " (%)"] = st.column_config.NumberColumn(nome + " %", format="%.2f%%")

        # A KEY única aqui é fundamental para o Streamlit Cloud não se perder na renderização
        st.dataframe(
            df_safra, 
            column_config=col_configs, 
            use_container_width=True, 
            hide_index=True,
            key=f"df_safra_{safra}_{i}"
        )
        st.divider()
else:
    st.warning("Sem dados para o intervalo selecionado.")
