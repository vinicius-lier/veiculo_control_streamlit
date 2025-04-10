import sqlite3
import logging
from utils.constants import ERRO_CONEXAO_DB, ERRO_EXECUCAO_DB

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de condutores
CREATE TABLE IF NOT EXISTS condutores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cnh TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    validade_cnh DATE NOT NULL,
    telefone TEXT NOT NULL,
    email TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de veículos
CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    ano INTEGER NOT NULL,
    placa TEXT NOT NULL UNIQUE,
    quilometragem INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'disponível',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de registros
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condutor_id INTEGER NOT NULL,
    veiculo_id INTEGER NOT NULL,
    data_saida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    km_saida INTEGER NOT NULL,
    checklist_saida TEXT NOT NULL,
    observacoes_saida TEXT,
    data_entrada TIMESTAMP,
    km_entrada INTEGER,
    checklist_entrada TEXT,
    observacoes_entrada TEXT,
    FOREIGN KEY (condutor_id) REFERENCES condutores(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);

-- Triggers para atualização automática de data_atualizacao
CREATE TRIGGER IF NOT EXISTS atualizar_condutor_data
AFTER UPDATE ON condutores
BEGIN
    UPDATE condutores 
    SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS atualizar_veiculo_data
AFTER UPDATE ON veiculos
BEGIN
    UPDATE veiculos 
    SET data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
"""

def criar_banco_dados(db_path: str = "database.db") -> None:
    """
    Cria o banco de dados e as tabelas necessárias.
    
    Args:
        db_path: Caminho do arquivo do banco de dados
        
    Raises:
        Exception: Se houver erro na criação do banco
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Executa os comandos SQL do schema
        cursor.executescript(SCHEMA_SQL)
        
        conn.commit()
        logger.info("Banco de dados criado/atualizado com sucesso")
        
    except Exception as e:
        logger.error(f"{ERRO_EXECUCAO_DB}: {str(e)}")
        raise Exception(ERRO_EXECUCAO_DB)
        
    finally:
        if conn:
            conn.close() 