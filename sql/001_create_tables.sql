CREATE TABLE IF NOT EXISTS pagamentos_agua (
    id              SERIAL PRIMARY KEY,
    nome_agente     VARCHAR(255) NOT NULL,
    mes_referencia  VARCHAR(7)   NOT NULL,
    valor           NUMERIC(10,2) NOT NULL DEFAULT 0,
    pago            BOOLEAN      NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)  NOT NULL DEFAULT 'NORMAL',
    criado_em       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome_agente, mes_referencia)
);

COMMENT ON TABLE pagamentos_agua IS 'Registros de pagamento de água dos Agentes da SMT';
COMMENT ON COLUMN pagamentos_agua.nome_agente IS 'Nome do agente';
COMMENT ON COLUMN pagamentos_agua.mes_referencia IS 'Mês de referência no formato YYYY-MM';
COMMENT ON COLUMN pagamentos_agua.valor IS 'Valor a ser pago pelo agente';
COMMENT ON COLUMN pagamentos_agua.pago IS 'Indica se o pagamento foi confirmado';
COMMENT ON COLUMN pagamentos_agua.status IS 'Situação do agente: NORMAL, FERIAS, LICENÇA';
