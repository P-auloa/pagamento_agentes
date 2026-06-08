import streamlit as st
import pandas as pd
from database import get_connection, buscar_dados
from components import (
    aplicar_estilo_escuro,
    renderizar_titulo,
    renderizar_avisos,
    renderizar_metricas,
    renderizar_tabela_pagamentos,
#   renderizar_grafico_mensal,
    renderizar_rodape,
    ordenar_meses,
)
from admin import renderizar_admin_area

st.set_page_config(
    page_title="AGTSMT - Controle de Água Mineral",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilo_escuro()
renderizar_titulo()
renderizar_avisos()

conn = get_connection()

try:
    df_completo = buscar_dados(conn)
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    df_completo = pd.DataFrame()

if not df_completo.empty:
    meses_disponiveis = ordenar_meses(df_completo["mes_referencia"].unique())

    st.subheader("Estou devendo esse mês?")
    mes_selecionado = st.selectbox(
        "Selecione o Mês que deseja ver:",
        meses_disponiveis,
        key="filtro_mes_usuario",
    )

    df_filtrado = df_completo[df_completo["mes_referencia"] == mes_selecionado]

    renderizar_metricas(df_filtrado)
    renderizar_tabela_pagamentos(df_filtrado, mes_selecionado)
#   renderizar_grafico_mensal(df_completo)
else:
    st.info("Nenhum registro encontrado no banco de dados.")

renderizar_rodape()

parametros = st.query_params
if "admin" in parametros and parametros["admin"] == "true":
    renderizar_admin_area(df_completo, conn)
