import streamlit as st
from sqlalchemy import text
from database import (
    verificar_registro_existente,
    inserir_registro,
    atualizar_pagamento,
    obter_agentes,
    obter_meses,
)


def _exibir_feedback():
    """Exibe mensagens de sucesso/erro armazenadas em session_state (persistem após rerun)"""
    if "admin_success" in st.session_state:
        st.success(st.session_state.admin_success)
        del st.session_state.admin_success

    if "admin_error" in st.session_state:
        st.error(st.session_state.admin_error)
        del st.session_state.admin_error


def renderizar_admin_area(df_completo, conn):
    """Renderiza a área administrativa com formulários de cadastro e atualização"""
    st.divider()
    st.markdown(
        '<h3 style="color: #ffb703;">🛠️ Área do Administrador</h3>',
        unsafe_allow_html=True,
    )

    _exibir_feedback()

    _renderizar_form_cadastro(conn)
    st.divider()
    _renderizar_form_atualizacao(conn, df_completo)


def _renderizar_form_cadastro(conn):
    """Formulário para cadastrar um novo registro de pagamento"""
    st.subheader("➕ Adicionar Novo Registro")

    with st.form("form_novo_registro"):
        col1, col2 = st.columns(2)

        with col1:
            agentes = obter_agentes(conn)
            if not agentes:
                st.info("Nenhum agente cadastrado ainda.")
                st.stop()

            novo_agente = st.selectbox(
                "Selecione o Agente", agentes, key="novo_agente_select"
            )

        with col2:
            meses = obter_meses(conn)
            mes_sel = st.selectbox("Escolha o mês:", meses, key="mes_referencia")

        col3, col4, col5 = st.columns(3)

        with col3:
       	    novo_valor = st.selectbox(
                "Valor (R$)", 
                options=[0, 10],
                format_func=lambda x: f"{x}.00"
            )

        with col4:
            novo_status = st.selectbox("Situação", ["NORMAL", "FERIAS", "LICENÇA"])

        with col5:
            novo_pago = st.toggle("Pagamento Confirmado")
            st.caption("✅ PAGO" if novo_pago else "❌ NÃO PAGO")

        botao_salvar = st.form_submit_button("Salvar Novo Registro")

        if botao_salvar:
            with conn.session as session:
                try:
                    if verificar_registro_existente(session, novo_agente, mes_sel):
                        st.session_state.admin_error = (
                            f"Já existe um registro para {novo_agente} no mês {mes_sel}."
                        )
                    else:
                        inserir_registro(
                            session, novo_agente, mes_sel, novo_valor, novo_pago, novo_status
                        )
                        st.session_state.admin_success = (
                            f"Registro de {novo_agente} para {mes_sel} cadastrado com sucesso!"
                        )
                    st.rerun()
                except Exception as e:
                    st.session_state.admin_error = f"Erro ao cadastrar: {e}"
                    st.rerun()


def _renderizar_form_atualizacao(conn, df_completo):
    """Formulário para atualizar o status de pagamento de um registro existente"""
    st.subheader("💰 Atualizar Pagamento")

    col_sel_A, col_sel_B = st.columns(2)

    with col_sel_A:
        agentes = sorted(df_completo["nome_agente"].unique())
        agente_sel = st.selectbox("Escolha o agente:", agentes, key="agente_update")

    with col_sel_B:
        meses = sorted(df_completo["mes_referencia"].unique())
        mes_sel = st.selectbox("Escolha o mês:", meses, key="mes_update")

    registro = df_completo[
        (df_completo["nome_agente"] == agente_sel)
        & (df_completo["mes_referencia"] == mes_sel)
    ]

    if not registro.empty:
        pago_atual = bool(registro["pago"].values[0])

        with st.form("form_update_pagamento"):
            novo_pagamento = st.toggle("Pagamento Confirmado", value=pago_atual)
            st.caption("✅ PAGO" if novo_pagamento else "❌ NÃO PAGO")

            botao_update = st.form_submit_button("Atualizar Pagamento")

            if botao_update:
                with conn.session as session:
                    try:
                        atualizar_pagamento(session, agente_sel, mes_sel, novo_pagamento)
                        st.session_state.admin_success = (
                            f"Pagamento de {agente_sel} ({mes_sel}) atualizado para "
                            f"{'PAGO' if novo_pagamento else 'NÃO PAGO'}!"
                        )
                        st.rerun()
                    except Exception as e:
                        st.session_state.admin_error = f"Erro ao atualizar: {e}"
                        st.rerun()
    else:
        st.warning("Nenhum registro encontrado para esse agente e mês.")
