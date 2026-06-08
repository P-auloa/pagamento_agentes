import streamlit as st
from sqlalchemy import text


def get_connection():
    """Retorna a conexão configurada com o PostgreSQL via Streamlit Secrets"""
    return st.connection("postgresql", type="sql")


def buscar_dados(conn):
    """Busca todos os registros da tabela pagamentos_agua ordenados por nome_agente"""
    return conn.query("SELECT * FROM pagamentos_agua ORDER BY nome_agente;", ttl="0")


def verificar_registro_existente(session, nome_agente, mes_referencia):
    """Verifica se já existe um registro para o agente no mês informado.
    Retorna True se existir, False caso contrário."""
    query = text("""
        SELECT COUNT(*)
        FROM pagamentos_agua
        WHERE nome_agente = :nome AND mes_referencia = :mes
    """)
    existe = session.execute(
        query, {"nome": nome_agente, "mes": mes_referencia}
    ).scalar()
    return existe > 0


def inserir_registro(session, nome_agente, mes_referencia, valor, pago, status):
    """Insere um novo registro de pagamento na tabela pagamentos_agua"""
    query = text("""
        INSERT INTO pagamentos_agua
            (nome_agente, mes_referencia, valor, pago, status)
        VALUES
            (:nome, :mes, :valor, :pago, :status)
    """)
    session.execute(
        query,
        {
            "nome": nome_agente,
            "mes": mes_referencia,
            "valor": valor,
            "pago": pago,
            "status": status,
        },
    )
    session.commit()


def atualizar_pagamento(session, nome_agente, mes_referencia, pago):
    """Atualiza apenas o campo pago de um registro existente"""
    query = text("""
        UPDATE pagamentos_agua
        SET pago = :pago
        WHERE nome_agente = :nome AND mes_referencia = :mes
    """)
    session.execute(
        query,
        {
            "pago": pago,
            "nome": nome_agente,
            "mes": mes_referencia,
        },
    )
    session.commit()


def obter_agentes(conn):
    """Retorna lista ordenada de agentes únicos cadastrados"""
    df = buscar_dados(conn)
    return sorted(df["nome_agente"].unique()) if not df.empty else []


def obter_meses(conn):
    """Retorna lista ordenada de meses de referência únicos cadastrados"""
    df = buscar_dados(conn)
    return sorted(df["mes_referencia"].unique()) if not df.empty else []
