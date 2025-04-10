from fpdf import FPDF
import os
from datetime import datetime

def gerar_pdf_saida(dados):
    """
    Gera um PDF com os dados do registro de saída
    
    Args:
        dados (dict): Dicionário com os dados do registro
            {
                'condutor': {'nome': str, 'cnh': str},
                'veiculo': {'marca': str, 'modelo': str, 'placa': str},
                'km_saida': int,
                'checklist': str,
                'observacoes': str
            }
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Configurações
    pdf.set_font('Arial', 'B', 16)
    
    # Cabeçalho
    pdf.cell(0, 10, 'REGISTRO DE SAÍDA DE VEÍCULO', ln=True, align='C')
    pdf.ln(10)
    
    # Data e hora
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True)
    pdf.ln(5)
    
    # Dados do condutor
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'DADOS DO CONDUTOR', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Nome: {dados["condutor"]["nome"]}', ln=True)
    pdf.cell(0, 10, f'CNH: {dados["condutor"]["cnh"]}', ln=True)
    pdf.ln(5)
    
    # Dados do veículo
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'DADOS DO VEÍCULO', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Marca/Modelo: {dados["veiculo"]["marca"]} {dados["veiculo"]["modelo"]}', ln=True)
    pdf.cell(0, 10, f'Placa: {dados["veiculo"]["placa"]}', ln=True)
    pdf.cell(0, 10, f'Quilometragem na saída: {dados["km_saida"]} km', ln=True)
    pdf.ln(5)
    
    # Checklist
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'CHECKLIST DE SAÍDA', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, dados['checklist'])
    pdf.ln(5)
    
    # Observações
    if dados.get('observacoes'):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'OBSERVAÇÕES', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, dados['observacoes'])
    
    # Assinatura
    pdf.ln(20)
    pdf.cell(0, 10, '_______________________', ln=True)
    pdf.cell(0, 10, 'Assinatura do Condutor', ln=True)
    
    # Salvar o PDF
    nome_arquivo = f"saida_{dados['veiculo']['placa']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_pdf = os.path.join('data', 'arquivos', 'pdfs', nome_arquivo)
    pdf.output(caminho_pdf)
    
    return caminho_pdf 