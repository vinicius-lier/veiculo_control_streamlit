CHECKLIST_SAIDA = {
    'Documentação': [
        'CNH em dia',
        'Documento do veículo em dia',
        'Seguro em dia'
    ],
    'Veículo': [
        'Combustível suficiente',
        'Pneus em bom estado',
        'Freios funcionando',
        'Óleo em nível adequado',
        'Água do radiador em nível',
        'Luzes funcionando',
        'Espelhos ajustados',
        'Capacete em bom estado'
    ],
    'Itens de Segurança': [
        'Capacete',
        'Luvas',
        'Jaqueta (se necessário)',
        'Botas apropriadas'
    ]
}

CHECKLIST_ENTRADA = {
    'Estado do Veículo': [
        'Combustível',
        'Quilometragem',
        'Danos/Arranhões',
        'Pneus',
        'Freios',
        'Óleo',
        'Água do radiador',
        'Luzes',
        'Espelhos'
    ],
    'Itens de Segurança': [
        'Capacete',
        'Luvas',
        'Jaqueta',
        'Botas'
    ],
    'Documentação': [
        'Documento do veículo',
        'Multas (se houver)'
    ]
}

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