import redis
import json

# Configuração do Redis
redis_client = redis.Redis(
    host='evolved-garfish-57315.upstash.io',
    port=6379,
    password='Ad_jAAIncDFmZDE3YzI5N2M1NDU0NzE5YWVlOTQwOWE1ZTI4Yjk3Y3AxNTczMTU',
    ssl=True
)

def save_data(key, data):
    """Salva dados no Redis"""
    try:
        redis_client.set(key, json.dumps(data))
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {str(e)}")
        return False

def get_data(key):
    """Recupera dados do Redis"""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Erro ao recuperar dados: {str(e)}")
        return None 