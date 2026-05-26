import streamlit as st

#"1. config da página"
st.set_page_config(page_title="Controle da Coleta de ÀGUA MINERAL", layout="wide")
st.title("Painel de controle - Pagamento de água")

#"2. Conexão com o banco de dados (postgreSQL do Supabase"
# O Streamlit lê as credenciais automaticamente do arquivo de segredos (secrets)
conn = st.connection("postgresql", type="sql")

#3. função para ler os dados do banco
def buscar_dados():
    return conn.query("SELECT * FROM pagamentos_agua ORDER BY nome_agente;", ttl="0")

df = buscar_dados()

#- --- interface do dasboard ---
# KPI (métricas resumidas)
total_pago = df[df['pago'] == True]['valor'].sum()
pendentes = df[df['pago'] == False]['nome_agente'].count()

col1, col2 = st.columns(2)
col1.metric(label="Total coletado do Mês", value=f"R$ {total_pago:.2f}")
col2.metric(label="Agentes Pendentes", value=str(pendentes))

st.divider()

#exibição de dados em tabela
st.subheader("Lista de registros")
st.dataframe(df, use_container_width=True)

st.divider()

#formulário de inserir novo pagamento (como escrever no banco de dados)
st.subheader("+ registrar novo pagamento")
with st.form("formulario_pagamento", clear_on_submit=True):
    nome = st.text_input("Nome do agente")
    mes = st.selectbox("Mês de referência", ["maio/2026", "junho/2026", "julho/2026"])
    valor = st.number_input("valor pago", min_value=0.0, value=30.0, step=5.0)
    status_pago = st.checkbox("Pagamento confirmado", value=True)

    botao_enviar = st.form_submit_button("Enviar pro banco de dados")

    if botao_enviar and nome:
        #query para inserir dados com segurança contra SQL injection
        query_insert = """
            INSERT INTO pagamentos_agua (nome_agente, mes_referencia, valor, pago)
            VALUES (:nome, :mes, :valor, :pago);
        """
        with conn.session as session:
            session.execute(query_insert, {"nome": nome, "mes": mes, "valor": valor, "pago": status_pago})
            session.commit()
        st.sucess(f"Pagamento de {nome} registrado com sucesso!")
        st.rerun()
