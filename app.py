import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Crédito Rural", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    arquivos = [
        "matriz_de_dados_credito_rural_2015-2016.parquet",
        "matriz_de_dados_credito_rural_2016-2017.parquet",
        "matriz_de_dados_credito_rural_2017-2018.parquet",
        "matriz_de_dados_credito_rural_2018-2019.parquet",
        "matriz_de_dados_credito_rural_2019-2020.parquet",
        "matriz_de_dados_credito_rural_2020-2021.parquet",
        "matriz_de_dados_credito_rural_2021-2022.parquet",
        "matriz_de_dados_credito_rural_2022-2023.parquet",
        "matriz_de_dados_credito_rural_2023-2024.parquet",
        "matriz_de_dados_credito_rural_2024-2025.parquet",
        "matriz_de_dados_credito_rural_2025-2026.parquet"
    ]
    
    lista_dfs = []
    for arq in arquivos:
        if os.path.exists(arq):
            try:
                df_temp = pd.read_parquet(arq)
                lista_dfs.append(df_temp)
            except Exception as e:
                st.warning(f"Aviso: Não foi possível ler {arq}. Erro: {e}", key=f"warn_{arq}")

    if not lista_dfs:
        st.error("Nenhum dos arquivos especificados foi encontrado no repositório.", key="error_no_files")
        return pd.DataFrame()

    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.rename(columns={
        'Classificacao_IF': 'Instituição Financeira',
        'Ano_Safra': 'Ano Safra'
    })
    df[['UF', 'Instituição Financeira', 'Ano Safra']] = df[['UF', 'Instituição Financeira', 'Ano Safra']].astype('category')
    df[['Mes_Emissao', 'Ano_Emissao']] = df[['Mes_Emissao', 'Ano_Emissao']].astype(int)
    return df

df = load_data()
if df.empty:
    st.stop()

# --- Configurações de Variáveis ---
valores_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
anos_safra = sorted(df['Ano Safra'].unique().tolist())

# --- Sidebar ---
st.sidebar.header("🔍 Filtros Estratégicos")
tema = st.sidebar.radio("Tema Visual", ["Claro", "Dark"])
inst_sel = st.sidebar.multiselect("Instituições", sorted(df['Instituição Financeira'].unique()))
safra_sel = st.sidebar.multiselect("Safras", anos_safra, default=[anos_safra[-1]])

# --- CSS e Tema ---
if tema == "Dark":
    bg_color, text_color, card_color, plotly_template = "#0E1117", "#FFFFFF", "#262730", "plotly_dark"
else:
    bg_color, text_color, card_color, plotly_template = "#FFFFFF", "#000000", "#F0F2F6", "plotly_white"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    [data-testid="stSidebar"] {{ background-color: {card_color}; }}
    h1, h2, h3, h5, p {{ color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- Cabeçalho ---
st.title("🌱 Inteligência do Crédito Rural")
st.markdown("##### Fonte: Banco Central do Brasil", key="md_fonte")

# --- Lógica de Meses da Safra ---
ordem_safra = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
nomes_meses = {7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez", 1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun"}

mes_inicio_nome, mes_fim_nome = st.sidebar.select_slider(
    "Intervalo de meses (Safra)",
    options=[nomes_meses[m] for m in ordem_safra],
    value=("Jul", "Jun")
)

mes_inicio = [k for k, v in nomes_meses.items() if v == mes_inicio_nome][0]
mes_fim = [k for k, v in nomes_meses.items() if v == mes_fim_nome][0]
idx_i, idx_f = ordem_safra.index(mes_inicio), ordem_safra.index(mes_fim)
meses_validos = ordem_safra[idx_i : idx_f + 1] if idx_i <= idx_f else ordem_safra[idx_i:] + ordem_safra[:idx_f + 1]

st.info(f"📅 Safra: **{mes_inicio_nome}** até **{mes_fim_nome}**", key="info_safra")
st.divider(key="divider_top")

# --- Filtros de Dados ---
df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel: df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel: df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- Visualizações ---
if not df_f.empty:
    # 1. Gráfico de Evolução
    st.subheader("📈 Evolução Mensal")
    evol_data = (
        df_f.groupby(['Instituição Financeira', 'Ano Safra', 'Mes_Emissao'], observed=True)[valores_cols]
        .sum()
        .sum(axis=1)
        .reset_index(name='Total')
    )
    evol_data['Total_BI'] = evol_data['Total'] / 1e9

    chart_key = f"chart_line_prod_{hash(str(safra_sel)+str(inst_sel)+str(mes_inicio_nome)+str(mes_fim_nome))}"
    fig_line = px.line(
        evol_data,
        x='Mes_Emissao',
        y='Total_BI',
        color='Instituição Financeira',
        facet_col='Ano Safra',
        markers=True,
        category_orders={"Mes_Emissao": ordem_safra},
        template=plotly_template
    )
    st.plotly_chart(fig_line, use_container_width=True, key=chart_key)

    # 2. Relatório de Finalidade
    st.subheader("📋 Detalhamento por Safra")
    rel_bruto = df_f.groupby(['Ano Safra', 'Instituição Financeira'], observed=True)[valores_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    rel_pct = (rel_bruto.div(rel_bruto.groupby(level=0).sum(), level=0) * 100)
    rel_pct.columns = [c + " (%)" for c in rel_pct.columns]

    df_final = pd.concat([rel_bruto / 1e9, rel_pct], axis=1).reset_index()

    for i, safra in enumerate(sorted(df_final['Ano Safra'].unique(), reverse=True)):
        st.markdown(f"#### 🗓️ Safra {safra}", key=f"md_safra_{safra}_{i}")
        df_safra = df_final[df_final['Ano Safra'] == safra].sort_values(by='Total', ascending=False)

        col_configs = {
            "Ano Safra": None,
            "Total": st.column_config.NumberColumn("Total", format="R$ %.2f BI"),
            "Total (%)": st.column_config.ProgressColumn("MS (%)", format="%.2f%%", min_value=0, max_value=100)
        }

        tbl_key = f"tbl_{safra}_{i}_{hash(str(df_safra.shape))}"
        st.dataframe(df_safra, column_config=col_configs, use_container_width=True, hide_index=True, key=tbl_key)

    st.divider(key="divider_final")
else:
    st.warning("Nenhum dado encontrado para os filtros atuais.", key="warn_no_data")
