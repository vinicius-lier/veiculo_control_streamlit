import redis
import json
import bcrypt
from datetime import datetime
import os

# Conexão com Redis Upstash
redis_client = redis.Redis(
    host='evolved-garfish-57315.upstash.io',
    port=6379,
    password='Ad_jAAIncDFmZDE3YzI5N2M1NDU0NzE5YWVlOTQwOWE1ZTI4Yjk3Y3AxNTczMTU',
    ssl=True,
    decode_responses=True
)

def init_db():
    """Inicializa o banco de dados com usuário admin se não existir"""
    if not redis_client.exists('users'):
        # Senha padrão: admin123
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        admin_user = {
            'username': 'admin',
            'password': hashed.decode('utf-8'),
            'role': 'admin'
        }
        redis_client.hset('users', 'admin', json.dumps(admin_user))

def create_user(username, password):
    """Cria um novo usuário"""
    if redis_client.hexists('users', username):
        return False, "Usuário já existe"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        'username': username,
        'password': hashed.decode('utf-8'),
        'role': 'user'
    }
    redis_client.hset('users', username, json.dumps(user))
    return True, "Usuário criado com sucesso"

def verify_user(username, password):
    """Verifica as credenciais do usuário"""
    user_data = redis_client.hget('users', username)
    if not user_data:
        return False, None
    
    user = json.loads(user_data)
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return True, user
    return False, None

def register_driver(driver_data):
    """Registra um novo condutor"""
    driver_id = f"driver_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    driver_data['status'] = 'ativo'
    driver_data['data_registro'] = datetime.now().isoformat()
    redis_client.hset('drivers', driver_id, json.dumps(driver_data))
    return driver_id

def get_driver(driver_id):
    """Retorna os dados de um condutor"""
    driver_data = redis_client.hget('drivers', driver_id)
    return json.loads(driver_data) if driver_data else None

def get_all_drivers():
    """Retorna todos os condutores"""
    drivers = redis_client.hgetall('drivers')
    return {k: json.loads(v) for k, v in drivers.items()}

def check_driver_has_active_vehicle(driver_id):
    """Verifica se o condutor tem veículo em uso"""
    exits = redis_client.hgetall('vehicle_exits')
    for exit_data in exits.values():
        exit_data = json.loads(exit_data)
        if exit_data['driver_id'] == driver_id and exit_data['status'] == 'em_uso':
            return True
    return False

def register_vehicle_exit(data):
    """Registra a saída de um veículo"""
    # Verificar se o condutor tem veículo em uso
    if check_driver_has_active_vehicle(data['driver_id']):
        return None, "Condutor já possui um veículo em uso"
    
    exit_id = f"exit_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    data['status'] = 'em_uso'
    data['data_saida'] = datetime.now().isoformat()
    redis_client.hset('vehicle_exits', exit_id, json.dumps(data))
    return exit_id, "Saída registrada com sucesso"

def get_active_exits():
    """Retorna todas as saídas ativas"""
    exits = redis_client.hgetall('vehicle_exits')
    return {k: json.loads(v) for k, v in exits.items() if json.loads(v)['status'] == 'em_uso'}

def register_vehicle_return(exit_id, data):
    """Registra o retorno de um veículo"""
    exit_data = redis_client.hget('vehicle_exits', exit_id)
    if not exit_data:
        return False, "Saída não encontrada"
    
    exit_data = json.loads(exit_data)
    if exit_data['status'] != 'em_uso':
        return False, "Veículo já retornado"
    
    exit_data.update(data)
    exit_data['status'] = 'retornado'
    exit_data['data_retorno'] = datetime.now().isoformat()
    redis_client.hset('vehicle_exits', exit_id, json.dumps(exit_data))
    return True, "Retorno registrado com sucesso"

def get_weekly_report():
    """Retorna os registros dos últimos 7 dias"""
    exits = redis_client.hgetall('vehicle_exits')
    all_exits = {k: json.loads(v) for k, v in exits.items()}
    
    # Filtrar últimos 7 dias
    seven_days_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)
    recent_exits = {
        k: v for k, v in all_exits.items()
        if datetime.fromisoformat(v['data_saida']).timestamp() > seven_days_ago
    }
    
    return recent_exits 