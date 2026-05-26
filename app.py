import streamlit as st

# 1. Configuração da página e Estilo Customizado (Cores vivas)
st.set_page_config(
    page_title="Controle de Água Interna", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Injeção de CSS para customizar as cores do dashboard (Tons de Azul e Verde)
st.markdown("""
    <style>
    /* Cor de fundo do app */
    .stApp {
        background-color: #f4f7f6;
    }
    /* Estilização dos blocos de métricas (Cards) */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #0077b6; /* Azul Água escuro */
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #4a4a4a;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Estilo para destacar títulos */
    .titulo-principal {
        color: #03045e;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        text-align: center;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título Estilizado
st.markdown('<h1 class="titulo-principal">💧 Painel de Controle - Coleta de Água</h1>', unsafe_allow_html=True)

# 2. Conexão com o Banco de Dados
conn = st.connection("postgresql", type="sql")

def buscar_dados():
    return conn.query("SELECT * FROM pagamentos_agua ORDER BY nome_agente;", ttl="0")

# Tratamento para evitar que o app trave se o banco estiver vazio
try:
    df = buscar_dados()
except Exception:
    df = None

# --- RENDERIZAÇÃO DAS MÉTRICAS (VISUAL EM CARDS COLORED) ---
if df is not null and not df.empty:
    # Cálculos
    total_pago = df[df['pago'] == True]['valor'].sum()
    pendentes = df[df['pago'] == False]['nome_agente'].count()
    
    # Criando colunas para os Cards de Destaque
    m1, m2 = st.columns(2)
    
    with m1:
        st.markdown(
            f"""
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 6px solid #2196f3; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:12px; color:#1565c0; font-weight:bold; text-transform:uppercase;">Arrecadado no Mês</p>
                <h2 style="margin:0; color:#0d47a1;">R$ {total_pago:,.2f}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with m2:
        # Se não houver pendentes, o card fica verde, se houver, fica laranja
        cor_fundo = "#e8f5e9" if pendentes == 0 else "#fff3e0"
        cor_borda = "#4caf50" if pendentes == 0 else "#ff9800"
        cor_texto = "#2e7d32" if pendentes == 0 else "#e65100"
        
        st.markdown(
            f"""
            <div style="background-color: {cor_fundo}; padding: 20px; border-radius: 10px; border-left: 6px solid {cor_borda}; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:12px; color:{cor_texto}; font-weight:bold; text-transform:uppercase;">Moradores Pendentes</p>
                <h2 style="margin:0; color:{cor_texto};">{pendentes}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Exibição dos Dados em Tabela Moderna
    st.subheader("📋 Lista Geral de Recebimentos")
    
    # Colorindo as linhas da tabela de forma interativa no Streamlit
    def colorir_status(val):
        color = '#c8e6c9' if val == True else '#ffcdd2'
        return f'background-color: {color}'
        
    st.dataframe(
        df.style.map(colorir_status, subset=['pago']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhum registro de pagamento encontrado no banco de dados.")

# --- CAMADA DE SEGURANÇA: CONTROLE DE ACESSO VIA URL ---
# O Streamlit lê os parâmetros após a '?' do link (Ex: ?admin=true)
parametros = st.query_params

if "admin" in parametros and parametros["admin"] == "true":
    st.divider()
    st.markdown('<h3 style="color: #e65100;">🛠️ Área do Administrador - Registrar Pagamento</h3>', unsafe_allow_html=True)
    
    with st.form("formulario_pagamento", clear_on_submit=True):
        col_nome, col_mes, col_val = st.columns([2, 1, 1])
        
        with col_nome:
            nome = st.text_input("Nome do Morador")
        with col_mes:
            mes = st.selectbox("Mês de Referência", ["Maio/2026", "Junho/2026", "Julho/2026"])
        with col_val:
            valor = st.number_input("Valor Pago", min_value=0.0, value=30.0, step=5.0)
            
        status_pago = st.checkbox("Confirmar Pagamento Realizado", value=True)
        botao_enviar = st.form_submit_button("Salvar no Banco de Dados")
        
        if botao_enviar and nome:
            query_insert = """
                INSERT INTO pagamentos_agua (nome_agente, mes_referencia, valor, pago)
                VALUES (:nome, :mes, :valor, :pago);
            """
            with conn.session as session:
                session.execute(query_insert, {"nome": nome, "mes": mes, "valor": valor, "pago": status_pago})
                session.commit()
            st.success(f"Sucesso! O pagamento de {nome} foi registrado.")
            st.rerun()