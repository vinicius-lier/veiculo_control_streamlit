import sqlite3
import os
from datetime import datetime

# Caminho do banco de dados
DB_PATH = os.path.join('data', 'veiculos.db')

def get_connection():
    """Cria uma conexão com o banco de dados"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Criar tabela de condutores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS condutores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cnh_numero TEXT UNIQUE NOT NULL,
        cnh_validade DATE NOT NULL,
        telefone TEXT NOT NULL,
        cnh_arquivo TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        placa TEXT UNIQUE NOT NULL,
        quilometragem_atual INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('disponivel', 'em uso'))
    )
    ''')
    
    # Criar tabela de registros
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        condutor_id INTEGER NOT NULL,
        veiculo_id INTEGER NOT NULL,
        data_saida DATETIME NOT NULL,
        data_entrada DATETIME,
        km_saida INTEGER NOT NULL,
        km_entrada INTEGER,
        checklist_saida TEXT NOT NULL,
        checklist_entrada TEXT,
        observacoes TEXT,
        pdf_saida TEXT NOT NULL,
        FOREIGN KEY (condutor_id) REFERENCES condutores (id),
        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def verificar_condutor_disponivel(condutor_id):
    """Verifica se um condutor tem algum registro em aberto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT COUNT(*) FROM registros 
    WHERE condutor_id = ? AND data_entrada IS NULL
    ''', (condutor_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count == 0

def verificar_veiculo_disponivel(veiculo_id):
    """Verifica se um veículo está disponível"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT status FROM veiculos WHERE id = ?', (veiculo_id,))
    status = cursor.fetchone()[0]
    conn.close()
    
    return status == 'disponivel'

# Inicializar o banco de dados quando o módulo for importado
if not os.path.exists('data'):
    os.makedirs('data')
init_db() 