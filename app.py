import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Configuração da Página (Estática e fixa) ---
st.set_page_config(
    page_title="Dashboard Crédito Rural", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Carga de Dados Robusta ---
@st.cache_data
def load_data_production():
    # Lista explícita dos arquivos para garantir a ordem e existência
    arquivos = [f"matriz_de_dados_credito_rural_{ano}-{ano+1}.parquet" for ano in range(2015, 2025)]
    
    lista_dfs = []
    for arq in arquivos:
        if os.path.exists(arq):
            try:
                temp = pd.read_parquet(arq)
                # Garante que as colunas de merge existam e sejam strings
                temp['Ano_Safra'] = temp['Ano_Safra'].astype(str)
                temp['Classificacao_IF'] = temp['Classificacao_IF'].astype(str)
                lista_dfs.append(temp)
            except Exception as e:
                st.sidebar.error(f"Erro ao ler {arq}: {e}")
                continue
    
    if not lista_dfs:
        return pd.DataFrame()
        
    df = pd.concat(lista_dfs, ignore_index=True)
    
    # Renomeação padrão
    df = df.rename(columns={
        'Classificacao_IF': 'Instituição Financeira',
        'Ano_Safra': 'Ano Safra'
    })
    
    return df

# Execução da carga
df = load_data_production()

if df.empty:
    st.error("Nenhum arquivo Parquet foi encontrado na raiz do projeto. Verifique o repositório.")
    st.stop()

# --- 3. Sidebar (Filtros com Keys Estáticas) ---
with st.sidebar:
    st.title("🌱 Filtros")
    
    instituicoes = sorted(df['Instituição Financeira'].unique())
    inst_sel = st.multiselect("Instituições", instituicoes, key="prod_inst_sel")
    
    safras_disponiveis = sorted(df['Ano Safra'].unique())
    safra_sel = st.multiselect(
        "Safras", 
        safras_disponiveis, 
        default=[safras_disponiveis[-1]] if safras_disponiveis else [],
        key="prod_safra_sel"
    )

    st.divider()
    
    # Lógica de meses da safra
    ordem_safra = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    nomes_meses = {7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez", 1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun"}
    
    mes_inicio_n, mes_fim_n = st.select_slider(
        "Intervalo de Meses (Safra)", 
        options=[nomes_meses[m] for m in ordem_safra], 
        value=("Jul", "Jun"),
        key="prod_mes_slider"
    )

# --- 4. Processamento de Filtros ---
mes_i = [k for k, v in nomes_meses.items() if v == mes_inicio_n][0]
mes_f = [k for k, v in nomes_meses.items() if v == mes_fim_n][0]
idx_i, idx_f = ordem_safra.index(mes_i), ordem_safra.index(mes_f)
meses_validos = ordem_safra[idx_i : idx_f + 1] if idx_i <= idx_f else ordem_safra[idx_i:] + ordem_safra[:idx_f + 1]

# Aplicando filtros no DataFrame
df_f = df[df['Mes_Emissao'].isin(meses_validos)].copy()
if safra_sel:
    df_f = df_f[df_f['Ano Safra'].isin(safra_sel)]
if inst_sel:
    df_f = df_f[df_f['Instituição Financeira'].isin(inst_sel)]

# --- 5. Área Principal ---
st.header("Intelligence Crédito Rural")
st.caption("Dados oficiais do Banco Central do Brasil")

if not df_f.empty:
    # --- Gráfico de Evolução ---
    with st.container():
        st.subheader("📈 Evolução Mensal")
        v_cols = ['Valor_Custeio', 'Valor_Investimento', 'Valor_Comercializacao', 'Valor_Industrializacao']
        
        evol = df_f.groupby(['Instituição Financeira', 'Ano Safra', 'Mes_Emissao'])[v_cols].sum().sum(axis=1).reset_index(name='Total')
        evol['Total_BI'] = evol['Total'] / 1e9

        fig = px.line(
            evol, x='Mes_Emissao', y='Total_BI', color='Instituição Financeira', 
            facet_col='Ano Safra', markers=True,
            category_orders={"Mes_Emissao": ordem_safra},
            labels={"Total_BI": "Bilhões (R$)", "Mes_Emissao": "Mês"},
            template="plotly_white"
        )
        # Key única evita que o gráfico cause erro ao ser removido/adicionado
        st.plotly_chart(fig, use_container_width=True, key="main_evolution_chart")

    st.divider()

    # --- Tabelas de Dados ---
    st.subheader("📋 Relatórios por Safra")
    
    rel_bruto = df_f.groupby(['Ano Safra', 'Instituição Financeira'])[v_cols].sum()
    rel_bruto['Total'] = rel_bruto.sum(axis=1)
    df_rel = (rel_bruto / 1e9).reset_index()

    # Renderização um por um para garantir estabilidade do nó
    for safra in sorted(df_rel['Ano Safra'].unique(), reverse=True):
        st.markdown(f"#### Safra {safra}")
        df_temp = df_rel[df_rel['Ano Safra'] == safra].sort_values('Total', ascending=False)
        
        st.dataframe(
            df_temp,
            column_config={
                "Total": st.column_config.NumberColumn("Total", format="R$ %.2f BI"),
                "Valor_Custeio": st.column_config.NumberColumn("Custeio", format="R$ %.2f BI"),
                "Valor_Investimento": st.column_config.NumberColumn("Invest.", format="R$ %.2f BI")
            },
            use_container_width=True,
            hide_index=True,
            key=f"table_final_{safra}"
        )
else:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")

# --- Rodapé ---
st.markdown("---")
st.markdown("Para alterar o tema (Claro/Escuro), use o menu do Streamlit no canto superior direito: **Settings > Theme**.")