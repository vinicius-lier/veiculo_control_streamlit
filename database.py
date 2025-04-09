import sqlite3
import bcrypt
from datetime import datetime
import os

def hash_password(password):
    # Gera um salt e faz o hash da senha
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    # Verifica se a senha corresponde ao hash
    return bcrypt.checkpw(password.encode(), hashed)

# Conexão com SQLite
def get_db():
    db = sqlite3.connect('vehicles.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    db = get_db()
    cursor = db.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de condutores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        document TEXT NOT NULL,
        status TEXT NOT NULL,
        data_registro TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de saídas de veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_exits (
        id TEXT PRIMARY KEY,
        driver_id TEXT NOT NULL,
        vehicle_plate TEXT NOT NULL,
        destination TEXT NOT NULL,
        status TEXT NOT NULL,
        data_saida TEXT NOT NULL,
        data_retorno TEXT,
        observations TEXT,
        FOREIGN KEY (driver_id) REFERENCES drivers (id)
    )
    ''')
    
    # Verificar se existe usuário admin
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Senha padrão: admin123
        hashed = hash_password('admin123')
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      ('admin', hashed, 'admin'))
    
    db.commit()
    db.close()

def create_user(username, password):
    """Cria um novo usuário"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        db.close()
        return False, "Usuário já existe"
    
    hashed = hash_password(password)
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, hashed, 'user'))
    
    db.commit()
    db.close()
    return True, "Usuário criado com sucesso"

def verify_user(username, password):
    """Verifica as credenciais do usuário"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    db.close()
    
    if not user:
        return False, None
    
    if verify_password(password, user['password']):
        return True, dict(user)
    return False, None

def register_driver(driver_data):
    """Registra um novo condutor"""
    db = get_db()
    cursor = db.cursor()
    
    driver_id = f"driver_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cursor.execute('''
    INSERT INTO drivers (id, name, document, status, data_registro)
    VALUES (?, ?, ?, ?, ?)
    ''', (driver_id, driver_data['name'], driver_data['document'], 
          'ativo', datetime.now().isoformat()))
    
    db.commit()
    db.close()
    return driver_id

def get_driver(driver_id):
    """Retorna os dados de um condutor"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
    driver = cursor.fetchone()
    db.close()
    
    return dict(driver) if driver else None

def get_all_drivers():
    """Retorna todos os condutores"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM drivers')
    drivers = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in drivers}

def check_driver_has_active_vehicle(driver_id):
    """Verifica se o condutor tem veículo em uso"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT * FROM vehicle_exits 
    WHERE driver_id = ? AND status = 'em_uso'
    ''', (driver_id,))
    
    has_active = bool(cursor.fetchone())
    db.close()
    return has_active

def register_vehicle_exit(data):
    """Registra a saída de um veículo"""
    if check_driver_has_active_vehicle(data['driver_id']):
        return None, "Condutor já possui um veículo em uso"
    
    db = get_db()
    cursor = db.cursor()
    
    exit_id = f"exit_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cursor.execute('''
    INSERT INTO vehicle_exits 
    (id, driver_id, vehicle_plate, destination, status, data_saida)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (exit_id, data['driver_id'], data['vehicle_plate'], 
          data['destination'], 'em_uso', datetime.now().isoformat()))
    
    db.commit()
    db.close()
    return exit_id, "Saída registrada com sucesso"

def get_active_exits():
    """Retorna todas as saídas ativas"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM vehicle_exits WHERE status = ?', ('em_uso',))
    exits = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in exits}

def register_vehicle_return(exit_id, data):
    """Registra o retorno de um veículo"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM vehicle_exits WHERE id = ?', (exit_id,))
    exit_data = cursor.fetchone()
    
    if not exit_data:
        db.close()
        return False, "Saída não encontrada"
    
    if exit_data['status'] != 'em_uso':
        db.close()
        return False, "Veículo já retornado"
    
    cursor.execute('''
    UPDATE vehicle_exits 
    SET status = ?, data_retorno = ?, observations = ?
    WHERE id = ?
    ''', ('retornado', datetime.now().isoformat(), 
          data.get('observations', ''), exit_id))
    
    db.commit()
    db.close()
    return True, "Retorno registrado com sucesso"

def get_weekly_report():
    """Retorna os registros dos últimos 7 dias"""
    db = get_db()
    cursor = db.cursor()
    
    seven_days_ago = (datetime.now().timestamp() - (7 * 24 * 60 * 60))
    cursor.execute('''
    SELECT * FROM vehicle_exits 
    WHERE datetime(data_saida) > datetime(?)
    ''', (datetime.fromtimestamp(seven_days_ago).isoformat(),))
    
    exits = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in exits} 