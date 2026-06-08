import streamlit as st
import pandas as pd
import altair as alt


def aplicar_estilo_escuro():
    """Injeta CSS customizado para tema escuro de alto contraste"""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        h1, h2, h3, p, span {
            color: #f0ffff !important;
        }
        .metric-card-pago {
            background-color: #1f2937 !important;
            padding: 20px;
            border-radius: 10px;
            border-left: 8px solid #00b4d8;
            box-shadow: 0px 4px 15px rgba(0, 180, 216, 0.25);
        }
        .metric-card-pendente {
            background-color: #1f2937 !important;
            padding: 20px;
            border-radius: 10px;
            border-left: 8px solid #ff4b4b;
            box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.25);
        }
        .titulo-principal {
            color: #00b4d8;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 800;
            text-align: center;
            padding-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_titulo():
    """Renderiza o título principal da página"""
    st.markdown(
        '<h1 class="titulo-principal">Controle de Pagamentos - Coleta de Água</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p style="color: #f0ffff; font-size: 16px; text-align: center; margin-bottom: 20px;">
        Controle de arrecadação da coleta de água dos Agentes da SMT. Verifique e lembre sua GU de fazer o pagamento. <br>
        Por enquanto, somente informações de quem e quanto foi arrecadado.
        Futuramente teremos os gastos com água no mês.
        </p>
        """,
        unsafe_allow_html=True,
    )


def renderizar_avisos():
    """Renderiza os avisos fixos para os usuários"""
    st.warning("⚠️ **LEMBRE DE FAZER O PIX NO QRCODE PERTO DO GALÃO**")
    st.divider()
    st.warning("DIA 10/06 irei adicionar quem ainda está faltanto pagar!")
    st.divider()


def renderizar_metricas(df_filtrado):
    """Exibe cartões com total arrecadado e quantidade de pendentes no mês filtrado"""
    total_pago = df_filtrado[df_filtrado["pago"] == True]["valor"].sum()
    pendentes = df_filtrado[df_filtrado["pago"] == False]["nome_agente"].count()

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card-pago">
                <p style="margin:0; font-size:13px; color:#00b4d8; font-weight:bold; text-transform:uppercase;">Arrecadado no Mês</p>
                <h2 style="margin:0; color:#ffffff; font-size:32px;">R$ {total_pago:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card-pendente">
                <p style="margin:0; font-size:13px; color:#ff4b4b; font-weight:bold; text-transform:uppercase;">Quantidade de Agentes Pendentes</p>
                <h2 style="margin:0; color:#ffffff; font-size:32px;">{pendentes}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)


def renderizar_tabela_pagamentos(df_filtrado, mes_selecionado):
    """Exibe a tabela de adimplentes com destaque colorido para pagamento"""
    st.subheader(f"Lista dos Adimplentes — {mes_selecionado}")
    st.caption("🟢 Verde: PAGOU  |  🔴 Vermelho: NÃO PAGOU")

    colunas_exibicao = ["nome_agente", "mes_referencia", "status", "pago"]
    df_tabela = df_filtrado[colunas_exibicao].copy()
    df_tabela.columns = ["Agente", "Mês", "Situação do Agente", "Pagamento"]

    def colorir_status(val):
        color = "#1b4d3e" if val == True else "#4a1515"
        return f"background-color: {color}; color: #ffffff;"

    st.dataframe(
        df_tabela.style.map(colorir_status, subset=["Pagamento"]),
        use_container_width=True,
        hide_index=True,
    )


def renderizar_grafico_mensal(df_completo):
    """Exibe gráfico de linhas (dupla escala) com valor arrecadado e agentes pendentes por mês"""
    st.subheader("Evolução Mensal")

    arrecadado_por_mes = (
        df_completo[df_completo["pago"] == True]
        .groupby("mes_referencia")["valor"]
        .sum()
        .reset_index()
        .rename(columns={"valor": "arrecadado"})
    )

    pendentes_por_mes = (
        df_completo[df_completo["pago"] == False]
        .groupby("mes_referencia")
        .size()
        .reset_index(name="pendentes")
    )

    chart_data = arrecadado_por_mes.merge(
        pendentes_por_mes, on="mes_referencia", how="outer"
    ).fillna(0)

    if chart_data.empty:
        st.info("Dados insuficientes para gerar o gráfico mensal.")
        return

    base = alt.Chart(chart_data).encode(
        x=alt.X("mes_referencia:O", title="Mês", sort=None)
    )

    linha_arrecadado = base.mark_line(stroke="#00b4d8", point=True).encode(
        y=alt.Y(
            "arrecadado:Q",
            axis=alt.Axis(
                title="Valor Arrecadado (R$)", titleColor="#00b4d8"
            ),
            scale=alt.Scale(zero=False),
        ),
        color=alt.value("#00b4d8"),
    )

    linha_pendentes = base.mark_line(stroke="#ff4b4b", point=True).encode(
        y=alt.Y(
            "pendentes:Q",
            axis=alt.Axis(
                title="Agentes Pendentes", titleColor="#ff4b4b"
            ),
            scale=alt.Scale(zero=False),
        ),
        color=alt.value("#ff4b4b"),
    )

    chart = (
        alt.layer(linha_arrecadado, linha_pendentes)
        .resolve_scale(y="independent")
        .configure_view(strokeWidth=0)
        .configure_legend(disable=True)
    )

    st.altair_chart(chart, use_container_width=True)


def renderizar_rodape():
    """Renderiza o rodapé informativo da página"""
    st.markdown(
        """
        <p style="color: #f0ffff; font-size: 12px; text-align: center; margin-top: 30px;">
        Qualquer erro, ausência de pagamentos ou situação especial: por favor, informe o ANDRADE para atualizar o registro. <br>
        Sou humano e esqueço das coisas kkkkkk
        </p>
        """,
        unsafe_allow_html=True,
    )
