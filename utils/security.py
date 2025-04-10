import bcrypt
import jwt
import datetime
import os
import logging
from typing import Dict, Any
from utils.common import logger

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'sua_chave_secreta_aqui')
        self.token_expiry = datetime.timedelta(hours=8)
    
    def hash_password(self, password: str) -> str:
        """Gera um hash seguro da senha usando bcrypt"""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao gerar hash da senha: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha em texto plano corresponde ao hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {str(e)}")
            return False
    
    def generate_token(self, user_data):
        """Gera um token JWT com os dados do usuário."""
        try:
            payload = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'role': user_data['role'],
                'exp': datetime.datetime.utcnow() + self.token_expiry
            }
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            logger.info(f"Token gerado para o usuário {user_data['username']}")
            return token
        except Exception as e:
            logger.error(f"Erro ao gerar token: {str(e)}")
            raise
    
    def verify_token(self, token):
        """Verifica se um token JWT é válido."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            logger.info(f"Token verificado para o usuário {payload['username']}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Token inválido: {str(e)}")
            raise
    
    def validate_session(self, session_state) -> bool:
        """Valida a sessão do usuário"""
        try:
            if 'token' not in session_state:
                return False
                
            token_data = self.verify_token(session_state.token)
            
            # Verifica se os dados do token correspondem aos da sessão
            return (
                token_data.get('user_id') == session_state.user_id and
                token_data.get('username') == session_state.username and
                token_data.get('role') == session_state.role
            )
        except Exception as e:
            logger.error(f"Erro ao validar sessão: {str(e)}")
            return False
    
    def check_permission(self, user_role, required_role):
        """Verifica se o usuário tem a permissão necessária."""
        role_levels = {
            'admin': 3,
            'gerente': 2,
            'usuario': 1
        }
        
        user_level = role_levels.get(user_role, 0)
        required_level = role_levels.get(required_role, 0)
        
        return user_level >= required_level
    
    def audit_log(self, user_id, action, details=None):
        """Registra uma ação no log de auditoria"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} - User ID: {user_id} - Action: {action}"
            if details:
                log_entry += f" - Details: {details}"
            
            logger.info(log_entry)
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar log de auditoria: {str(e)}")
            return False
    
    def require_role(self, required_role):
        """Decorator para verificar permissão de acesso"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # TODO: Implementar verificação de role
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Instância global do gerenciador de segurança
security_manager = SecurityManager() 