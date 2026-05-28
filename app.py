import streamlit as st
import pandas as pd

# 1. Configuração da página e Estilo Customizado
st.set_page_config(
    page_title="AGTSMT - Controle de Água Mineral", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Injeção de CSS para Tema Escuro de Alto Contraste
st.markdown("""
    <style>
    /* Forçar o fundo escuro do aplicativo */
    .stApp {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    
    /* Garantir que textos e títulos fiquem claros */
    h1, h2, h3, p, span {
        color: #f0ffff !important;
    }

    /* Card Pago: Fundo grafite, borda azul neon e sombra brilhante */
    .metric-card-pago {
        background-color: #1f2937 !important; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #00b4d8; 
        box-shadow: 0px 4px 15px rgba(0, 180, 216, 0.25);
    }
    
    /* Card Pendente: Fundo grafite, borda laranja/vermelha e sombra quente */
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
    """, unsafe_allow_html=True)


# Título e Subtítulos Estilizados (CORREÇÃO: alterado a cor do texto do parágrafo para clara #f0ffff)
st.markdown('<h1 class="titulo-principal">Controle de Pagamentos - Coleta de Água</h1>', unsafe_allow_html=True)
st.markdown("""
    <p style="color: #f0ffff; font-size: 16px; text-align: center; margin-bottom: 20px;">
    Controle de arrecadação da coleta de água dos Agentes da SMT. Verifique e lembre sua GU de fazer o pagamento. <br>
    Por enquanto, somente informações de quem e quanto foi arrecadado.
    Futuramente teremos os gastos com água no mês.
    </p>
    """, unsafe_allow_html=True)

st.warning("⚠️ **LEMBRE DE FAZER O PIX NO QRCODE PERTO DO GALÃO**")
st.divider()

# 2. Conexão com o Banco de Dados
conn = st.connection("postgresql", type="sql")

def buscar_dados():
    return conn.query("SELECT * FROM pagamentos_agua ORDER BY nome_agente;", ttl="0")

try:
    df_completo = buscar_dados()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    df_completo = pd.DataFrame()

if not df_completo.empty:
    
    # --- CAMADA DE FILTRAGEM POR MÊS ---
    meses_disponiveis = sorted(df_completo['mes_referencia'].unique())
    
    st.subheader("Estou devendo esse mês?")
    mes_selecionado = st.selectbox("Selecione o Mês que deseja ver:", meses_disponiveis, key="filtro_mes_usuario")
    
    df_filtrado = df_completo[df_completo['mes_referencia'] == mes_selecionado]

    # --- RENDERIZAÇÃO DAS MÉTRICAS ---
    total_pago = df_filtrado[df_filtrado['pago'] == True]['valor'].sum()
    pendentes = df_filtrado[df_filtrado['pago'] == False]['nome_agente'].count()
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card-pago">
                <p style="margin:0; font-size:13px; color:#00b4d8; font-weight:bold; text-transform:uppercase;">Arrecadado no Mês</p>
                <h2 style="margin:0; color:#ffffff; font-size:32px;">R$ {total_pago:,.2f}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with m2:
        st.markdown(
            f"""
            <div class="metric-card-pendente">
                <p style="margin:0; font-size:13px; color:#ff4b4b; font-weight:bold; text-transform:uppercase;">Quantidade de Agentes Pendentes</p>
                <h2 style="margin:0; color:#ffffff; font-size:32px;">{pendentes}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- EXIBIÇÃO DA TABELA ---
    st.subheader(f"Lista dos Adimplentes — {mes_selecionado}")
    st.caption("🟢 Verde: PAGOU  |  🔴 Vermelho: NÃO PAGOU")
    
    colunas_exibicao = ['nome_agente', 'mes_referencia', 'status', 'pago']
    df_tabela = df_filtrado[colunas_exibicao].copy()
    df_tabela.columns = ['Agente', 'Mês', 'Situação do Agente', 'Pagamento']
    
    def colorir_status(val):
        color = '#1b4d3e' if val == True else '#4a1515'
        return f'background-color: {color}; color: #ffffff;'
        
    st.dataframe(
        df_tabela.style.map(colorir_status, subset=['Pagamento']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhum registro encontrado no banco de dados.")

st.markdown("""
    <p style="color: #f0ffff; font-size: 12px; text-align: center; margin-top: 30px;">
    Qualquer erro, ausência de pagamentos ou situação especial: por favor, informe o ANDRADE para atualizar o registro. <br>
    Sou humano e esqueço das coisas kkkkkk
    </p>
    """, unsafe_allow_html=True)


# --- ÁREA DO ADMINISTRADOR (NOVA VERSÃO) ---
parametros = st.query_params

if "admin" in parametros and parametros["admin"] == "true":
    st.divider()
    st.markdown(
        '<h3 style="color: #ffb703;">🛠️ Área do Administrador</h3>',
        unsafe_allow_html=True
    )

    from sqlalchemy import text

    # =========================================================
    # ABA 1 — CADASTRAR NOVO REGISTRO
    # =========================================================

    st.subheader("➕ Adicionar Novo Registro")

    with st.form("form_novo_registro"):

        col1, col2 = st.columns(2)

        with col1:

           lista_agentes_existentes = sorted(
               df_completo['nome_agente'].unique()
           )

           novo_agente = st.selectbox(
               "Selecione o Agente",
               lista_agentes_existentes,
               key="novo_agente_select"
           )

        with col2:
            lista_meses = sorted(
                df_completo['mes_referencia'].unique()
            )

            mes_sel = st.selectbox(
                "Escolha o mês:",
                lista_meses,
                key="mes_referencia"
            )

        col3, col4, col5 = st.columns(3)
            
        with col3:
            novo_valor = st.number_input(
                "Valor",
                min_value=10.0,
            )

        with col4:
            novo_status = st.selectbox(
                "Situação",
                ["NORMAL", "FERIAS", "LICENÇA"]
            )

        with col5:
            novo_pago = st.checkbox("Pagamento Confirmado")

        botao_salvar_novo = st.form_submit_button("Salvar Novo Registro")

        if botao_salvar_novo:

            # Verifica se já existe registro
            query_verifica = text("""
                SELECT COUNT(*) 
                FROM pagamentos_agua
                WHERE nome_agente = :nome
                AND mes_referencia = :mes
            """)

            with conn.session as session:

                existe = session.execute(
                    query_verifica,
                    {
                        "nome": novo_agente,
                        "mes": mes_sel
                    }
                ).scalar()

                if existe > 0:
                    st.warning(
                        "Já existe um registro para esse agente nesse mês."
                    )

                else:

                    query_insert = text("""
                        INSERT INTO pagamentos_agua
                        (
                            nome_agente,
                            mes_referencia,
                            valor,
                            pago,
                            status
                        )
                        VALUES
                        (
                            :nome,
                            :mes,
                            :valor,
                            :pago,
                            :status
                        )
                    """)

                    session.execute(
                        query_insert,
                        {
                            "nome": novo_agente,
                            "mes": mes_sel,
                            "valor": novo_valor,
                            "pago": novo_pago,
                            "status": novo_status
                        }
                    )

                    session.commit()

                    st.success("Novo registro cadastrado com sucesso!")
                    st.rerun()

    st.divider()

    # =========================================================
    # ABA 2 — ALTERAR SOMENTE PAGAMENTO
    # =========================================================

    st.subheader("💰 Atualizar Pagamento")

    if not df_completo.empty:

        col_sel_A, col_sel_B = st.columns(2)

        with col_sel_A:
            lista_agentes = sorted(
                df_completo['nome_agente'].unique()
            )

            agente_sel = st.selectbox(
                "Escolha o agente:",
                lista_agentes,
                key="agente_update"
            )

        with col_sel_B:
            lista_meses = sorted(
                df_completo['mes_referencia'].unique()
            )

            mes_sel = st.selectbox(
                "Escolha o mês:",
                lista_meses,
                key="mes_update"
            )

        registro = df_completo[
            (df_completo['nome_agente'] == agente_sel) &
            (df_completo['mes_referencia'] == mes_sel)
        ]

        if not registro.empty:

            pago_atual = bool(registro['pago'].values[0])

            with st.form("form_update_pagamento"):

                novo_pagamento = st.checkbox(
                    "Pagamento Confirmado",
                    value=pago_atual
                )

                botao_update = st.form_submit_button(
                    "Atualizar Pagamento"
                )

                if botao_update:

                    query_update = text("""
                        UPDATE pagamentos_agua
                        SET pago = :pago
                        WHERE nome_agente = :nome
                        AND mes_referencia = :mes
                    """)

                    with conn.session as session:

                        session.execute(
                            query_update,
                            {
                                "pago": novo_pagamento,
                                "nome": agente_sel,
                                "mes": mes_sel
                            }
                        )

                        session.commit()

                    st.success(
                        f"Pagamento de {agente_sel} atualizado!"
                    )

                    st.rerun()

        else:
            st.warning("Registro não encontrado.")