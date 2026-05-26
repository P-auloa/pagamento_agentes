import streamlit as st
import pandas as pd

# 1. Configuração da página e Estilo Customizado
st.set_page_config(
    page_title=" AGTSMT - Controle de Água Mineral", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #0077b6; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #4a4a4a; text-transform: uppercase; letter-spacing: 1px; }
    .titulo-principal { color: #03045e; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Título e Subtítulos Estilizados
st.markdown('<h1 class="titulo-principal">Controle de Pagamentos - Coleta de Água</h1>', unsafe_allow_html=True)
st.markdown("""
    <p style="color: #2b2d42; font-size: 16px; text-align: center; margin-bottom: 20px;">
    Controle de arrecadação da coleta de água dos Agentes da SMT. Verifique e lembre sua GU de fazer o pagamento. 
    Por enquanto, somente informações de quem arrecadou.
    Futuramente irei colocar os gastos com água no mês.
    
    </p>
    """, unsafe_allow_html=True)

st.warning("⚠️ **LEMBRE DE FAZER O PIX NO QRCODE PERTO DO GALÃO**")
st.divider()

# 2. Conexão com o Banco de Dados
conn = st.connection("postgresql", type="sql")

def buscar_dados():
    # Busca todas as informações para podermos tratar os filtros no Python
    return conn.query("SELECT * FROM pagamentos_agua ORDER BY nome_agente;", ttl="0")

try:
    df_completo = buscar_dados()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    df_completo = pd.DataFrame()

if not df_completo.empty:
    
    # --- CAMADA DE FILTRAGEM POR MÊS ---
    # Captura todos os meses únicos existentes no banco para gerar as opções do filtro
    meses_disponiveis = sorted(df_completo['mes_referencia'].unique())
    
    st.subheader("Estou devendo esse mês?")
    mes_selecionado = st.selectbox("Selecione o Mês que deseja ver:", meses_disponiveis)
    
    # Filtrando o DataFrame baseado na escolha do usuário
    df_filtrado = df_completo[df_completo['mes_referencia'] == mes_selecionado]

    # --- RENDERIZAÇÃO DAS MÉTRICAS (BASEADO NO MÊS FILTRADO) ---
    total_pago = df_filtrado[df_filtrado['pago'] == True]['valor'].sum()
    pendentes = df_filtrado[df_filtrado['pago'] == False]['nome_agente'].count()
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 6px solid #2196f3; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:12px; color:#1565c0; font-weight:bold; text-transform:uppercase;"> Total arrecadado em {mes_selecionado}</p>
                <h2 style="margin:0; color:#0d47a1;">R$ {total_pago:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
    with m2:
        cor_fundo = "#e8f5e9" if pendentes == 0 else "#fff3e0"
        cor_borda = "#4caf50" if pendentes == 0 else "#ff9800"
        cor_texto = "#2e7d32" if pendentes == 0 else "#e65100"
        st.markdown(f"""
            <div style="background-color: {cor_fundo}; padding: 20px; border-radius: 10px; border-left: 6px solid {cor_borda}; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size:12px; color:{cor_texto}; font-weight:bold; text-transform:uppercase;">Agentes Pendentes em ({mes_selecionado})</p>
                <h2 style="margin:0; color:{cor_texto};">{pendentes}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- EXIBIÇÃO DA TABELA (APENAS AS COLUNAS SOLICITADAS) ---
    st.subheader(f"Quem ta em dia e quem ta inadimplente — {mes_selecionado}")
    st.subheader(f"Verde ta pago - Vermelho ta devendo")
    
    # Mapeamento exato das colunas que você quer exibir (Garante a ordem e o filtro das colunas)
    # Nota: Certifique-se de que o nome da coluna de status no seu banco seja exatamente 'status'
    colunas_exibicao = ['nome_agente', 'mes_referencia', 'status', 'pago']
    
    df_tabela = df_filtrado[colunas_exibicao].copy()
    
    # Renomeando os cabeçalhos para ficar amigável no site
    df_tabela.columns = ['Agente', 'Mês', 'Situação do Agente', 'Pagamento']
    
    def colorir_status(val):
        color = '#c8e6c9' if val == True else '#ffcdd2'
        return f'background-color: {color}'
        
    st.dataframe(
        df_tabela.style.map(colorir_status, subset=['Pagamento']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhum registro encontrado no banco de dados.")

st.markdown("""
    <p style="color: #2b2d42; font-size: 12px; text-align: center; margin-bottom: 20px;">
    Qualquer erro, ausência de pagamentos ou situação especial: lembre o ANDRADE de atualizar o registro.
    Sou humano e esqueço das coisas kkkkkk
    
    </p>
    """, unsafe_allow_html=True)

# --- ÁREA DO ADMINISTRADOR (ATUALIZAÇÃO DE REGISTROS) ---
parametros = st.query_params

if "admin" in parametros and parametros["admin"] == "true" and not df_completo.empty:
    st.divider()
    st.markdown('<h3 style="color: #e65100;">🛠️ Área do Administrador — Atualizar Cadastro / Pagamento</h3>', unsafe_allow_html=True)
    
    with st.form("formulario_admin", clear_on_submit=False):
        col_A, col_B, col_C, col_D = st.columns(4)
        
        with col_A:
            # Pega a lista de agentes cadastrados para virar um campo de seleção
            lista_agentes = sorted(df_completo['nome_agente'].unique())
            agente_sel = st.selectbox("Selecione o Agente:", lista_agentes)
            
        with col_B:
            # Seleciona qual mês você quer alterar o registro daquele agente
            lista_meses_form = sorted(df_completo['mes_referencia'].unique())
            mes_sel = st.selectbox("Mês de Referência:", lista_meses_form)
            
        with col_C:
            # Permite alterar a situação do agente (Férias, Normal, Licença)
            situacao_atual = st.selectbox("Situação Atual do Agente:", ["Normal", "Férias", "Licença"])
            
        with col_D:
            # Lê o estado atual do banco para já vir marcado ou não (Melhoria de usabilidade)
            registro_atual = df_completo[(df_completo['nome_agente'] == agente_sel) & (df_completo['mes_referencia'] == mes_sel)]
            pago_padrao = bool(registro_atual['pago'].values[0]) if not registro_atual.empty else False
            
            status_pago = st.checkbox("Pagamento Confirmado", value=pago_padrao)
            
        botao_atualizar = st.form_submit_button("Salvar Alterações")
        
        if botao_atualizar:
            # Comando UPDATE para modificar a linha existente baseando-se no Agente e no Mês selecionados
            query_update = """
                UPDATE pagamentos_agua 
                SET pago = :pago, status = :status
                WHERE nome_agente = :nome AND mes_referencia = :mes;
            """
            with conn.session as session:
                session.execute(query_update, {
                    "pago": status_pago, 
                    "status": situacao_atual, 
                    "nome": agente_sel, 
                    "mes": mes_sel
                })
                session.commit()
            st.success(f"Dados do agente {agente_sel} atualizados com sucesso para o mês {mes_sel}!")
            st.rerun()
