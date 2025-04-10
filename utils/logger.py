import logging
import os
from datetime import datetime
from utils.constants import DIR_LOGS

def setup_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger com as configurações padrão.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        
    Returns:
        Logger configurado
    """
    # Cria o diretório de logs se não existir
    if not os.path.exists(DIR_LOGS):
        os.makedirs(DIR_LOGS)
        
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evita duplicação de handlers
    if not logger.handlers:
        # Handler para arquivo
        log_file = os.path.join(DIR_LOGS, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Registra um erro no log com contexto adicional.
    
    Args:
        logger: Logger configurado
        error: Exceção ocorrida
        context: Contexto adicional do erro
    """
    error_msg = f"{context + ' - ' if context else ''}{str(error)}"
    logger.error(error_msg, exc_info=True)

def log_info(logger: logging.Logger, message: str) -> None:
    """
    Registra uma mensagem informativa no log.
    
    Args:
        logger: Logger configurado
        message: Mensagem a ser registrada
    """
    logger.info(message)

def log_warning(logger: logging.Logger, message: str) -> None:
    """
    Registra um aviso no log.
    
    Args:
        logger: Logger configurado
        message: Mensagem de aviso
    """
    logger.warning(message)

# Configura o logger para o Streamlit
streamlit_logger = logging.getLogger('streamlit')
streamlit_logger.setLevel(logging.WARNING)

# Configura o logger para o SQLite
sqlite_logger = logging.getLogger('sqlite3')
sqlite_logger.setLevel(logging.WARNING)

def get_logger(nome: str) -> logging.Logger:
    """
    Retorna um logger configurado com o nome especificado.
    
    Args:
        nome: Nome do logger
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(nome) 