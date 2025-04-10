import os
from datetime import datetime
from fpdf import FPDF
from utils.constants import (
    DIRETORIO_PDFS,
    ERRO_GERACAO_PDF,
    ERRO_SALVAMENTO_PDF,
    ERRO_CRIACAO_DIRETORIO
)

class PDFGenerator:
    def __init__(self):
        self._criar_diretorio_pdfs()
        
    def _criar_diretorio_pdfs(self) -> None:
        """
        Cria o diretório para armazenar os PDFs se não existir.
        
        Raises:
            Exception: Se não conseguir criar o diretório
        """
        try:
            if not os.path.exists(DIRETORIO_PDFS):
                os.makedirs(DIRETORIO_PDFS)
        except Exception as e:
            raise Exception(f"{ERRO_CRIACAO_DIRETORIO}: {str(e)}")
            
    def gerar_pdf_saida(self, dados: dict) -> str:
        """
        Gera um PDF com os dados da saída do veículo.
        
        Args:
            dados: Dicionário com os dados da saída
            
        Returns:
            Caminho do arquivo PDF gerado
            
        Raises:
            Exception: Se houver erro na geração do PDF
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Configurações
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Registro de Saída de Veículo", ln=True, align="C")
            
            # Dados do condutor
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Dados do Condutor", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Nome: {dados['condutor_nome']}", ln=True)
            pdf.cell(0, 10, f"CNH: {dados['condutor_cnh']}", ln=True)
            
            # Dados do veículo
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Dados do Veículo", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Placa: {dados['veiculo_placa']}", ln=True)
            pdf.cell(0, 10, f"Modelo: {dados['veiculo_modelo']}", ln=True)
            pdf.cell(0, 10, f"Quilometragem: {dados['quilometragem']}", ln=True)
            
            # Data e hora
            pdf.cell(0, 10, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
            
            # Checklist
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Checklist", ln=True)
            pdf.set_font("Arial", "", 12)
            for item, status in dados['checklist'].items():
                pdf.cell(0, 10, f"{item}: {'OK' if status else 'NOK'}", ln=True)
                
            # Observações
            if dados.get('observacoes'):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Observações", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, dados['observacoes'])
                
            # Salva o PDF
            nome_arquivo = f"saida_{dados['veiculo_placa']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            caminho_arquivo = os.path.join(DIRETORIO_PDFS, nome_arquivo)
            pdf.output(caminho_arquivo)
            
            return caminho_arquivo
            
        except Exception as e:
            raise Exception(f"{ERRO_GERACAO_PDF}: {str(e)}")
            
    def gerar_pdf_entrada(self, dados: dict) -> str:
        """
        Gera um PDF com os dados da entrada do veículo.
        
        Args:
            dados: Dicionário com os dados da entrada
            
        Returns:
            Caminho do arquivo PDF gerado
            
        Raises:
            Exception: Se houver erro na geração do PDF
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Configurações
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Registro de Entrada de Veículo", ln=True, align="C")
            
            # Dados do veículo
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Dados do Veículo", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Placa: {dados['veiculo_placa']}", ln=True)
            pdf.cell(0, 10, f"Modelo: {dados['veiculo_modelo']}", ln=True)
            pdf.cell(0, 10, f"Quilometragem: {dados['quilometragem']}", ln=True)
            
            # Data e hora
            pdf.cell(0, 10, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
            
            # Checklist
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Checklist", ln=True)
            pdf.set_font("Arial", "", 12)
            for item, status in dados['checklist'].items():
                pdf.cell(0, 10, f"{item}: {'OK' if status else 'NOK'}", ln=True)
                
            # Observações
            if dados.get('observacoes'):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Observações", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, dados['observacoes'])
                
            # Salva o PDF
            nome_arquivo = f"entrada_{dados['veiculo_placa']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            caminho_arquivo = os.path.join(DIRETORIO_PDFS, nome_arquivo)
            pdf.output(caminho_arquivo)
            
            return caminho_arquivo
            
        except Exception as e:
            raise Exception(f"{ERRO_GERACAO_PDF}: {str(e)}") 