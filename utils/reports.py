import pandas as pd
from datetime import datetime, timedelta
from utils.db import get_connection
from utils.common import logger
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self, output_dir='data/relatorios'):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Garante que o diretório de relatórios existe"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Diretório de relatórios criado: {self.output_dir}")
    
    def _get_report_filename(self, tipo):
        """Gera nome do arquivo de relatório com timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"relatorio_{tipo}_{timestamp}.pdf"
    
    def gerar_relatorio_diario(self):
        """Gera relatório diário com estatísticas"""
        try:
            conn = get_connection()
            
            # Estatísticas gerais
            stats = pd.read_sql("""
                SELECT 
                    COUNT(*) as total_veiculos,
                    SUM(CASE WHEN status = 'disponivel' THEN 1 ELSE 0 END) as veiculos_disponiveis,
                    SUM(CASE WHEN status = 'em uso' THEN 1 ELSE 0 END) as veiculos_em_uso
                FROM veiculos
            """, conn)
            
            # Saídas do dia
            saidas = pd.read_sql("""
                SELECT 
                    v.placa,
                    c.nome as condutor,
                    r.data_saida,
                    r.km_saida,
                    r.km_entrada,
                    (r.km_entrada - r.km_saida) as km_percorridos
                FROM registros r
                JOIN veiculos v ON r.veiculo_id = v.id
                JOIN condutores c ON r.condutor_id = c.id
                WHERE DATE(r.data_saida) = DATE('now')
            """, conn)
            
            # Gerar gráficos
            fig_uso = px.pie(
                stats,
                values=[stats['veiculos_disponiveis'][0], stats['veiculos_em_uso'][0]],
                names=['Disponíveis', 'Em Uso'],
                title='Status dos Veículos'
            )
            
            if not saidas.empty:
                fig_km = px.bar(
                    saidas,
                    x='placa',
                    y='km_percorridos',
                    title='Quilometragem por Veículo',
                    labels={'placa': 'Placa', 'km_percorridos': 'KM Percorridos'}
                )
            else:
                fig_km = None
            
            # Gerar PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Relatório Diário - Controle de Veículos', ln=True, align='C')
            pdf.ln(10)
            
            # Data
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Data: {datetime.now().strftime("%d/%m/%Y")}', ln=True)
            pdf.ln(5)
            
            # Estatísticas
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Estatísticas Gerais', ln=True)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Total de Veículos: {stats["total_veiculos"][0]}', ln=True)
            pdf.cell(0, 10, f'Veículos Disponíveis: {stats["veiculos_disponiveis"][0]}', ln=True)
            pdf.cell(0, 10, f'Veículos em Uso: {stats["veiculos_em_uso"][0]}', ln=True)
            pdf.ln(5)
            
            # Saídas do dia
            if not saidas.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Saídas do Dia', ln=True)
                pdf.set_font('Arial', '', 12)
                
                for _, row in saidas.iterrows():
                    pdf.cell(0, 10, f'Placa: {row["placa"]}', ln=True)
                    pdf.cell(0, 10, f'Condutor: {row["condutor"]}', ln=True)
                    pdf.cell(0, 10, f'KM Percorridos: {row["km_percorridos"]}', ln=True)
                    pdf.ln(5)
            else:
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 10, 'Nenhuma saída registrada hoje.', ln=True)
            
            # Salvar PDF
            filename = self._get_report_filename('diario')
            pdf_path = os.path.join(self.output_dir, filename)
            pdf.output(pdf_path)
            
            logger.info(f"Relatório diário gerado com sucesso: {pdf_path}")
            return True, pdf_path
        except Exception as e:
            logger.error(f"Erro ao gerar relatório diário: {str(e)}")
            return False, f"Erro ao gerar relatório diário: {str(e)}"
        finally:
            conn.close()
    
    def gerar_relatorio_semanal(self):
        """Gera relatório semanal com estatísticas"""
        try:
            conn = get_connection()
            
            # Estatísticas da semana
            stats = pd.read_sql("""
                SELECT 
                    DATE(r.data_saida) as data,
                    COUNT(*) as total_saidas,
                    SUM(r.km_entrada - r.km_saida) as km_total
                FROM registros r
                WHERE DATE(r.data_saida) >= DATE('now', '-7 days')
                GROUP BY DATE(r.data_saida)
                ORDER BY data
            """, conn)
            
            # Top condutores
            top_condutores = pd.read_sql("""
                SELECT 
                    c.nome,
                    COUNT(*) as total_saidas,
                    SUM(r.km_entrada - r.km_saida) as km_total
                FROM registros r
                JOIN condutores c ON r.condutor_id = c.id
                WHERE DATE(r.data_saida) >= DATE('now', '-7 days')
                GROUP BY c.id, c.nome
                ORDER BY km_total DESC
                LIMIT 5
            """, conn)
            
            # Gerar gráficos
            if not stats.empty:
                fig_saidas = px.line(
                    stats,
                    x='data',
                    y='total_saidas',
                    title='Saídas por Dia',
                    labels={'data': 'Data', 'total_saidas': 'Total de Saídas'}
                )
                
                fig_km = px.line(
                    stats,
                    x='data',
                    y='km_total',
                    title='Quilometragem por Dia',
                    labels={'data': 'Data', 'km_total': 'KM Total'}
                )
            else:
                fig_saidas = None
                fig_km = None
            
            if not top_condutores.empty:
                fig_condutores = px.bar(
                    top_condutores,
                    x='nome',
                    y='km_total',
                    title='Top 5 Condutores por Quilometragem',
                    labels={'nome': 'Condutor', 'km_total': 'KM Total'}
                )
            else:
                fig_condutores = None
            
            # Gerar PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Relatório Semanal - Controle de Veículos', ln=True, align='C')
            pdf.ln(10)
            
            # Período
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Período: Últimos 7 dias', ln=True)
            pdf.ln(5)
            
            # Estatísticas
            if not stats.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Estatísticas da Semana', ln=True)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 10, f'Total de Saídas: {stats["total_saidas"].sum()}', ln=True)
                pdf.cell(0, 10, f'Quilometragem Total: {stats["km_total"].sum():.0f} km', ln=True)
                pdf.ln(5)
            
            # Top condutores
            if not top_condutores.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Top 5 Condutores', ln=True)
                pdf.set_font('Arial', '', 12)
                
                for _, row in top_condutores.iterrows():
                    pdf.cell(0, 10, f'Condutor: {row["nome"]}', ln=True)
                    pdf.cell(0, 10, f'Saídas: {row["total_saidas"]}', ln=True)
                    pdf.cell(0, 10, f'KM Total: {row["km_total"]:.0f}', ln=True)
                    pdf.ln(5)
            
            # Salvar PDF
            filename = self._get_report_filename('semanal')
            pdf_path = os.path.join(self.output_dir, filename)
            pdf.output(pdf_path)
            
            logger.info(f"Relatório semanal gerado com sucesso: {pdf_path}")
            return True, pdf_path
        except Exception as e:
            logger.error(f"Erro ao gerar relatório semanal: {str(e)}")
            return False, f"Erro ao gerar relatório semanal: {str(e)}"
        finally:
            conn.close()
    
    def gerar_relatorio_mensal(self):
        """Gera relatório mensal com estatísticas"""
        try:
            conn = get_connection()
            
            # Estatísticas do mês
            stats = pd.read_sql("""
                SELECT 
                    strftime('%Y-%m', r.data_saida) as mes,
                    COUNT(*) as total_saidas,
                    SUM(r.km_entrada - r.km_saida) as km_total,
                    COUNT(DISTINCT r.condutor_id) as total_condutores,
                    COUNT(DISTINCT r.veiculo_id) as total_veiculos
                FROM registros r
                WHERE strftime('%Y-%m', r.data_saida) = strftime('%Y-%m', 'now')
                GROUP BY strftime('%Y-%m', r.data_saida)
            """, conn)
            
            # Top veículos
            top_veiculos = pd.read_sql("""
                SELECT 
                    v.placa,
                    COUNT(*) as total_saidas,
                    SUM(r.km_entrada - r.km_saida) as km_total
                FROM registros r
                JOIN veiculos v ON r.veiculo_id = v.id
                WHERE strftime('%Y-%m', r.data_saida) = strftime('%Y-%m', 'now')
                GROUP BY v.id, v.placa
                ORDER BY km_total DESC
                LIMIT 5
            """, conn)
            
            # Gerar gráficos
            if not top_veiculos.empty:
                fig_veiculos = px.bar(
                    top_veiculos,
                    x='placa',
                    y='km_total',
                    title='Top 5 Veículos por Quilometragem',
                    labels={'placa': 'Placa', 'km_total': 'KM Total'}
                )
            else:
                fig_veiculos = None
            
            # Gerar PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Relatório Mensal - Controle de Veículos', ln=True, align='C')
            pdf.ln(10)
            
            # Mês
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Mês: {datetime.now().strftime("%B/%Y")}', ln=True)
            pdf.ln(5)
            
            # Estatísticas
            if not stats.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Estatísticas do Mês', ln=True)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 10, f'Total de Saídas: {stats["total_saidas"][0]}', ln=True)
                pdf.cell(0, 10, f'Quilometragem Total: {stats["km_total"][0]:.0f} km', ln=True)
                pdf.cell(0, 10, f'Total de Condutores: {stats["total_condutores"][0]}', ln=True)
                pdf.cell(0, 10, f'Total de Veículos: {stats["total_veiculos"][0]}', ln=True)
                pdf.ln(5)
            
            # Top veículos
            if not top_veiculos.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Top 5 Veículos', ln=True)
                pdf.set_font('Arial', '', 12)
                
                for _, row in top_veiculos.iterrows():
                    pdf.cell(0, 10, f'Placa: {row["placa"]}', ln=True)
                    pdf.cell(0, 10, f'Saídas: {row["total_saidas"]}', ln=True)
                    pdf.cell(0, 10, f'KM Total: {row["km_total"]:.0f}', ln=True)
                    pdf.ln(5)
            
            # Salvar PDF
            filename = self._get_report_filename('mensal')
            pdf_path = os.path.join(self.output_dir, filename)
            pdf.output(pdf_path)
            
            logger.info(f"Relatório mensal gerado com sucesso: {pdf_path}")
            return True, pdf_path
        except Exception as e:
            logger.error(f"Erro ao gerar relatório mensal: {str(e)}")
            return False, f"Erro ao gerar relatório mensal: {str(e)}"
        finally:
            conn.close() 