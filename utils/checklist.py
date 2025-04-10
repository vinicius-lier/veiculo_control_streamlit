from typing import Dict, List

class Checklist:
    def __init__(self):
        self._itens_saida = {
            "Documentação": [
                "CNH em dia",
                "Documento do veículo",
                "Seguro em dia"
            ],
            "Veículo": [
                "Combustível",
                "Óleo",
                "Água",
                "Pneus",
                "Freios",
                "Luzes",
                "Espelhos",
                "Limpeza"
            ],
            "Equipamentos": [
                "Capacete",
                "Luvas",
                "Jaqueta",
                "Botas"
            ]
        }
        
        self._itens_entrada = {
            "Veículo": [
                "Combustível",
                "Óleo",
                "Água",
                "Pneus",
                "Freios",
                "Luzes",
                "Espelhos",
                "Limpeza",
                "Danos"
            ],
            "Equipamentos": [
                "Capacete",
                "Luvas",
                "Jaqueta",
                "Botas"
            ]
        }
        
    def get_itens_saida(self) -> Dict[str, List[str]]:
        """
        Retorna os itens do checklist de saída.
        
        Returns:
            Dicionário com os itens do checklist
        """
        return self._itens_saida
        
    def get_itens_entrada(self) -> Dict[str, List[str]]:
        """
        Retorna os itens do checklist de entrada.
        
        Returns:
            Dicionário com os itens do checklist
        """
        return self._itens_entrada
        
    def validar_checklist(self, checklist: Dict[str, Dict[str, bool]]) -> bool:
        """
        Valida se todos os itens do checklist foram preenchidos.
        
        Args:
            checklist: Dicionário com os itens do checklist
            
        Returns:
            True se todos os itens foram preenchidos, False caso contrário
        """
        for categoria, itens in checklist.items():
            for item, status in itens.items():
                if status is None:
                    return False
        return True
        
    def formatar_checklist(self, checklist: Dict[str, Dict[str, bool]]) -> str:
        """
        Formata o checklist para exibição.
        
        Args:
            checklist: Dicionário com os itens do checklist
            
        Returns:
            String formatada com o checklist
        """
        texto = ""
        for categoria, itens in checklist.items():
            texto += f"\n{categoria}:\n"
            for item, status in itens.items():
                texto += f"- {item}: {'OK' if status else 'NOK'}\n"
        return texto

def get_checklist_options(tipo):
    """
    Retorna as opções do checklist baseado no tipo (saída ou entrada)
    
    Args:
        tipo (str): 'saida' ou 'entrada'
    
    Returns:
        dict: Dicionário com as opções do checklist
    """
    if tipo == 'saida':
        return CHECKLIST_SAIDA
    elif tipo == 'entrada':
        return CHECKLIST_ENTRADA
    else:
        raise ValueError("Tipo de checklist inválido. Use 'saida' ou 'entrada'.")

def get_checklist_saida():
    """
    Gera um formulário de checklist de saída e retorna o texto com os itens selecionados
    
    Returns:
        str: Texto com os itens selecionados no checklist
    """
    import streamlit as st
    
    checklist_selecionado = []
    
    for categoria, itens in CHECKLIST_SAIDA.items():
        st.write(f"**{categoria}**")
        for item in itens:
            if st.checkbox(item, key=f"saida_{item}"):
                checklist_selecionado.append(item)
    
    return "\n".join(checklist_selecionado)

def get_checklist_entrada():
    """
    Gera um formulário de checklist de entrada e retorna o texto com os itens selecionados
    
    Returns:
        str: Texto com os itens selecionados no checklist
    """
    import streamlit as st
    
    checklist_selecionado = []
    
    for categoria, itens in CHECKLIST_ENTRADA.items():
        st.write(f"**{categoria}**")
        for item in itens:
            if st.checkbox(item, key=f"entrada_{item}"):
                checklist_selecionado.append(item)
    
    return "\n".join(checklist_selecionado)

def get_checklist_saida_form():
    """
    Gera um formulário de checklist de saída para ser usado dentro de um st.form
    
    Returns:
        list: Lista com os itens selecionados no checklist
    """
    import streamlit as st
    
    checklist_selecionado = []
    
    for categoria, itens in CHECKLIST_SAIDA.items():
        st.write(f"**{categoria}**")
        for item in itens:
            if st.checkbox(item, key=f"saida_form_{item}"):
                checklist_selecionado.append(item)
    
    return checklist_selecionado

def get_checklist_entrada_form():
    """
    Gera um formulário de checklist de entrada para ser usado dentro de um st.form
    
    Returns:
        list: Lista com os itens selecionados no checklist
    """
    import streamlit as st
    
    checklist_selecionado = []
    
    for categoria, itens in CHECKLIST_ENTRADA.items():
        st.write(f"**{categoria}**")
        for item in itens:
            if st.checkbox(item, key=f"entrada_form_{item}"):
                checklist_selecionado.append(item)
    
    return checklist_selecionado 