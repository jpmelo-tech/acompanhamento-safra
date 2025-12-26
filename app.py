import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste leitura Parquet", page_icon="📂", layout="wide")
st.title("📂 Teste de leitura dos arquivos Parquet (raw GitHub)")

# Lista de anos e construção dos caminhos raw
base_url = "https://raw.githubusercontent.com/jpmelo-tech/acompanhamento-safra/main/"
anos = [
    "2015-2016","2016-2017","2017-2018","2018-2019","2019-2020",
    "2020-2021","2021-2022","2022-2023","2023-2024","2024-2025","2025-2026"
]
arquivos = [f"matriz_de_dados_credito_rural_{ano}.parquet" for ano in anos]

st.write("Iniciando leitura de arquivos...")

resultados = []
for i, arq in enumerate(arquivos, start=1):
    url = base_url + arq
    with st.spinner(f"Lendo {arq} ({i}/{len(arquivos)})..."):
        try:
            df_temp = pd.read_parquet(url)
            resultados.append({
                "arquivo": arq,
                "linhas": len(df_temp),
                "colunas": len(df_temp.columns),
                "ok": True
            })
        except Exception as e:
            resultados.append({
                "arquivo": arq,
                "linhas": None,
                "colunas": None,
                "ok": False,
                "erro": str(e)
            })

# Tabela de resultados
st.subheader("Resumo da leitura por arquivo")
st.dataframe(
    pd.DataFrame(resultados),
    use_container_width=True
)

# Mensagem final
total_ok = sum(r["ok"] for r in resultados)
st.success(f"Arquivos lidos com sucesso: {total_ok}/{len(resultados)}")
