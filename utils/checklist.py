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