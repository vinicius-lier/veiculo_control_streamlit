import streamlit as st
import logging
import os
from functools import wraps
from utils.security import SecurityManager
from datetime import datetime

# Configuração do logger
logger = logging.getLogger(__name__)

# Inicialização do gerenciador de segurança
security_manager = SecurityManager()

def setup_logging():
    """Configura o sistema de logging da aplicação."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def require_auth(func):
    """Decorator para verificar autenticação"""
    def wrapper(*args, **kwargs):
        if not security_manager.validate_session(st.session_state):
            st.error("Por favor, faça login para acessar esta página.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def setup_page(title, icon=None):
    """Configura a página do Streamlit"""
    if icon:
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide"
        )
    else:
        st.set_page_config(
            page_title=title,
            layout="wide"
        )

def show_error(message, error=None):
    """Exibe mensagem de erro e registra no log"""
    st.error(message)
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)

def show_success(message):
    """Exibe mensagem de sucesso e registra no log"""
    st.success(message)
    logger.info(message)

def audit_action(action, details=None):
    """Registra uma ação no log de auditoria"""
    if 'user_id' in st.session_state:
        security_manager.audit_log(
            st.session_state.user_id,
            action,
            details
        )

def format_datetime(dt):
    """Formata uma data/hora para exibição."""
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def format_currency(value):
    """Formata um valor monetário."""
    return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def validate_cpf(cpf):
    """Valida um número de CPF."""
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11:
        return False
        
    # Verifica se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False
        
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0
    if int(cpf[9]) != digito1:
        return False
        
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0
    if int(cpf[10]) != digito2:
        return False
        
    return True

def validate_cnh(cnh):
    """Valida um número de CNH."""
    # Remove caracteres não numéricos
    cnh = ''.join(filter(str.isdigit, cnh))
    
    if len(cnh) != 11:
        return False
        
    # Verifica se todos os dígitos são iguais
    if len(set(cnh)) == 1:
        return False
        
    return True

def validate_placa(placa):
    """Valida uma placa de veículo (formato Mercosul)."""
    import re
    padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'
    return bool(re.match(padrao, placa.upper()))

# Inicializa o logging
logger = setup_logging() 