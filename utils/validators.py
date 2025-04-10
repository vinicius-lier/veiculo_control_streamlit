import re
from datetime import datetime, date
from utils.common import logger
from utils.constants import (
    MIN_QUILOMETRAGEM,
    MAX_QUILOMETRAGEM,
    MIN_CARACTERES_SENHA,
    KM_MINIMO, KM_MAXIMO, TAMANHO_MINIMO_SENHA, TAMANHO_MAXIMO_SENHA,
    AVISO_KM_INVALIDA, AVISO_SENHA_INVALIDA, AVISO_EMAIL_INVALIDO,
    AVISO_TELEFONE_INVALIDO, AVISO_DATA_INVALIDA,
    AVISO_CNH_INVALIDA,
    ERRO_SENHA_INVALIDA,
    ERRO_EMAIL_INVALIDO,
    ERRO_TELEFONE_INVALIDO,
    ERRO_QUILOMETRAGEM_INVALIDA,
    ERRO_DATA_INVALIDA,
    ERRO_CNH_INVALIDA
)
from typing import Optional, Tuple

def validar_cnh(cnh):
    """
    Valida o formato da CNH
    Formato esperado: 11 dígitos numéricos
    """
    try:
        if not cnh or not cnh.isdigit() or len(cnh) != 11:
            logger.warning(f"CNH inválida: {cnh}")
            return False, "CNH deve conter 11 dígitos numéricos"
        return True, "CNH válida"
    except Exception as e:
        logger.error(f"Erro ao validar CNH: {str(e)}")
        return False, f"Erro ao validar CNH: {str(e)}"

def validar_placa(placa):
    """
    Valida o formato da placa
    Formatos aceitos: Mercosul (ABC1D23) ou antigo (ABC1234)
    """
    try:
        placa = placa.upper().strip()
        padrao_mercosul = re.compile(r'^[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}$')
        padrao_antigo = re.compile(r'^[A-Z]{3}[0-9]{4}$')
        
        if not (padrao_mercosul.match(placa) or padrao_antigo.match(placa)):
            logger.warning(f"Placa inválida: {placa}")
            return False, "Formato de placa inválido"
        return True, "Placa válida"
    except Exception as e:
        logger.error(f"Erro ao validar placa: {str(e)}")
        return False, f"Erro ao validar placa: {str(e)}"

def validar_quilometragem(km: int, km_anterior: int = None) -> tuple[bool, str]:
    """
    Valida se a quilometragem é válida.
    
    Args:
        km: Quilometragem a ser validada
        km_anterior: Quilometragem anterior (opcional)
        
    Returns:
        Tuple com (bool indicando se é válida, mensagem de erro)
    """
    if km < 0:
        return False, ERRO_QUILOMETRAGEM_INVALIDA
        
    if km_anterior is not None and km < km_anterior:
        return False, ERRO_QUILOMETRAGEM_INVALIDA
        
    return True, ""

def validar_data_validade(data_validade):
    """
    Valida a data de validade
    - Deve ser uma data futura
    - Deve estar no formato correto
    """
    try:
        if isinstance(data_validade, str):
            data_validade = datetime.strptime(data_validade, '%Y-%m-%d').date()
        
        if data_validade < date.today():
            logger.warning(f"Data de validade expirada: {data_validade}")
            return False, "Data de validade não pode ser no passado"
        
        return True, "Data de validade válida"
    except Exception as e:
        logger.error(f"Erro ao validar data de validade: {str(e)}")
        return False, f"Erro ao validar data de validade: {str(e)}"

def validar_telefone(telefone: str) -> tuple[bool, str]:
    """
    Valida se o telefone está em um formato válido.
    
    Args:
        telefone: Telefone a ser validado
        
    Returns:
        Tuple com (bool indicando se é válido, mensagem de erro)
    """
    # Remove caracteres não numéricos
    telefone = re.sub(r'\D', '', telefone)
    
    if len(telefone) < 10 or len(telefone) > 11:
        return False, ERRO_TELEFONE_INVALIDO
    return True, ""

def validar_nome(nome):
    """
    Valida o nome do condutor
    - Deve conter apenas letras, espaços e acentos
    - Deve ter pelo menos 3 caracteres
    """
    try:
        nome = nome.strip()
        if len(nome) < 3:
            logger.warning(f"Nome muito curto: {nome}")
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome):
            logger.warning(f"Nome contém caracteres inválidos: {nome}")
            return False, "Nome deve conter apenas letras e espaços"
        
        return True, "Nome válido"
    except Exception as e:
        logger.error(f"Erro ao validar nome: {str(e)}")
        return False, f"Erro ao validar nome: {str(e)}"

def validar_data(data: str) -> tuple[bool, str]:
    """
    Valida se a data está em um formato válido.
    
    Args:
        data: Data a ser validada (formato: DD/MM/AAAA)
        
    Returns:
        Tuple com (bool indicando se é válida, mensagem de erro)
    """
    try:
        datetime.strptime(data, '%d/%m/%Y')
        return True, ""
    except ValueError:
        return False, ERRO_DATA_INVALIDA

def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida se a senha atende aos requisitos mínimos.
    
    Args:
        senha: Senha a ser validada
        
    Returns:
        Tuple com (bool indicando se é válida, mensagem de erro)
    """
    if len(senha) < 8:
        return False, ERRO_SENHA_INVALIDA
        
    if not re.search(r"[A-Z]", senha):
        return False, ERRO_SENHA_INVALIDA
        
    if not re.search(r"[a-z]", senha):
        return False, ERRO_SENHA_INVALIDA
        
    if not re.search(r"\d", senha):
        return False, ERRO_SENHA_INVALIDA
        
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False, ERRO_SENHA_INVALIDA
        
    return True, ""

def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida se o email está em um formato válido.
    
    Args:
        email: Email a ser validado
        
    Returns:
        Tuple com (bool indicando se é válido, mensagem de erro)
    """
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email):
        return False, ERRO_EMAIL_INVALIDO
    return True, ""

def validar_cnh(cnh: str) -> tuple[bool, str]:
    """
    Valida se o número da CNH está em um formato válido.
    
    Args:
        cnh: Número da CNH a ser validado
        
    Returns:
        Tuple com (bool indicando se é válido, mensagem de erro)
    """
    # Remove caracteres não numéricos
    cnh = re.sub(r'\D', '', cnh)
    
    if len(cnh) != 11:
        return False, ERRO_CNH_INVALIDA
    return True, ""

def validar_placa(placa: str) -> Tuple[bool, str]:
    """
    Valida se a placa está em um formato válido.
    
    Args:
        placa: Placa a ser validada
        
    Returns:
        Tuple com (bool indicando se é válida, mensagem de erro)
    """
    # Formato antigo: ABC-1234
    # Formato Mercosul: ABC1D23
    padrao_antigo = r'^[A-Z]{3}-?\d{4}$'
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    
    placa = placa.upper()
    if not (re.match(padrao_antigo, placa) or re.match(padrao_mercosul, placa)):
        return False, "Placa inválida"
    return True, ""

def validar_ano(ano: int) -> Tuple[bool, str]:
    """
    Valida se o ano está em um intervalo válido.
    
    Args:
        ano: Ano a ser validado
        
    Returns:
        Tuple com (bool indicando se é válido, mensagem de erro)
    """
    ano_atual = datetime.now().year
    if ano < 1900 or ano > ano_atual + 1:
        return False, "Ano inválido"
    return True, "" 