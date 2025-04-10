import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from utils.auth import Auth
from utils.database import Database
from utils.checklist import Checklist
from utils.pdf_generator import PDFGenerator
from utils.validators import validar_quilometragem
from utils.constants import (
    TITULO_APP,
    ICONE_APP,
    SUCESSO_SAIDA,
    AVISO_CAMPO_OBRIGATORIO
)

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title=f"{TITULO_APP} - Registro de Saída",
    page_icon=ICONE_APP,
    layout="wide"
)

def get_condutores_disponiveis(db: Database) -> list:
    """
    Obtém a lista de condutores disponíveis.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        Lista de condutores disponíveis
    """
    try:
        condutores = db.execute_query("""
            SELECT 
                c.id,
                c.nome,
                c.cnh
            FROM condutores c
            LEFT JOIN registros r ON c.id = r.condutor_id
            WHERE r.data_entrada IS NOT NULL
            OR r.id IS NULL
            ORDER BY c.nome
        """)
        
        return condutores
    except Exception as e:
        logger.error(f"Erro ao obter condutores disponíveis: {str(e)}")
        return []

def get_veiculos_disponiveis(db: Database) -> list:
    """
    Obtém a lista de veículos disponíveis.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        Lista de veículos disponíveis
    """
    try:
        veiculos = db.execute_query("""
            SELECT 
                v.id,
                v.marca,
                v.modelo,
                v.placa,
                v.quilometragem
            FROM veiculos v
            LEFT JOIN registros r ON v.id = r.veiculo_id
            WHERE r.data_entrada IS NOT NULL
            OR r.id IS NULL
            ORDER BY v.marca, v.modelo
        """)
        
        return veiculos
    except Exception as e:
        logger.error(f"Erro ao obter veículos disponíveis: {str(e)}")
        return []

def registrar_saida(
    db: Database,
    condutor_id: int,
    veiculo_id: int,
    quilometragem: int,
    checklist: dict,
    observacoes: str = None
) -> tuple[bool, str]:
    """
    Registra a saída de um veículo.
    
    Args:
        db: Instância do banco de dados
        condutor_id: ID do condutor
        veiculo_id: ID do veículo
        quilometragem: Quilometragem de saída
        checklist: Checklist de saída
        observacoes: Observações (opcional)
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Validações
        if not all([condutor_id, veiculo_id, quilometragem]):
            return False, AVISO_CAMPO_OBRIGATORIO
            
        # Verifica se condutor está disponível
        condutor = db.execute_query("""
            SELECT c.* 
            FROM condutores c
            LEFT JOIN registros r ON c.id = r.condutor_id
            WHERE c.id = ?
            AND (r.data_entrada IS NOT NULL OR r.id IS NULL)
        """, (condutor_id,))
        
        if not condutor:
            return False, "Condutor não está disponível"
            
        # Verifica se veículo está disponível
        veiculo = db.execute_query("""
            SELECT v.*
            FROM veiculos v
            LEFT JOIN registros r ON v.id = r.veiculo_id
            WHERE v.id = ?
            AND (r.data_entrada IS NOT NULL OR r.id IS NULL)
        """, (veiculo_id,))
        
        if not veiculo:
            return False, "Veículo não está disponível"
            
        # Valida quilometragem
        valido, msg = validar_quilometragem(quilometragem, veiculo[0]['quilometragem'])
        if not valido:
            return False, msg
            
        # Registra saída
        query = """
            INSERT INTO registros (
                condutor_id, veiculo_id, data_saida,
                km_saida, checklist_saida, observacoes_saida
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            condutor_id,
            veiculo_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            quilometragem,
            str(checklist),
            observacoes
        ))
        
        # Atualiza quilometragem do veículo
        db.execute_query(
            "UPDATE veiculos SET quilometragem = ? WHERE id = ?",
            (quilometragem, veiculo_id)
        )
        
        # Gera PDF
        pdf = PDFGenerator()
        dados_pdf = {
            'condutor_nome': condutor[0]['nome'],
            'condutor_cnh': condutor[0]['cnh'],
            'veiculo_placa': veiculo[0]['placa'],
            'veiculo_modelo': f"{veiculo[0]['marca']} {veiculo[0]['modelo']}",
            'quilometragem': quilometragem,
            'checklist': checklist,
            'observacoes': observacoes
        }
        pdf.gerar_pdf_saida(dados_pdf)
        
        logger.info(f"Saída registrada: Condutor {condutor[0]['nome']}, Veículo {veiculo[0]['placa']}")
        return True, SUCESSO_SAIDA
        
    except Exception as e:
        logger.error(f"Erro ao registrar saída: {str(e)}")
        return False, str(e)

def main():
    """
    Função principal da página.
    """
    try:
        # Verifica autenticação
        auth = Auth()
        if not auth.verificar_autenticacao():
            st.switch_page("app.py")
            
        # Inicializa banco de dados e checklist
        db = Database()
        checklist = Checklist()
        
        # Título
        st.title("Registro de Saída")
        
        # Obtém condutores e veículos disponíveis
        condutores = get_condutores_disponiveis(db)
        veiculos = get_veiculos_disponiveis(db)
        
        if not condutores:
            st.warning("Não há condutores disponíveis")
            return
            
        if not veiculos:
            st.warning("Não há veículos disponíveis")
            return
            
        # Formulário
        with st.form("form_saida"):
            # Seleção de condutor e veículo
            col1, col2 = st.columns(2)
            
            with col1:
                condutor_id = st.selectbox(
                    "Condutor",
                    [c['id'] for c in condutores],
                    format_func=lambda x: next(
                        c['nome'] for c in condutores if c['id'] == x
                    )
                )
                
            with col2:
                veiculo_id = st.selectbox(
                    "Veículo",
                    [v['id'] for v in veiculos],
                    format_func=lambda x: f"{next(v['marca'] for v in veiculos if v['id'] == x)} {next(v['modelo'] for v in veiculos if v['id'] == x)} - {next(v['placa'] for v in veiculos if v['id'] == x)}"
                )
                
            # Quilometragem
            quilometragem = st.number_input(
                "Quilometragem de Saída",
                min_value=next(
                    v['quilometragem'] for v in veiculos if v['id'] == veiculo_id
                ),
                value=next(
                    v['quilometragem'] for v in veiculos if v['id'] == veiculo_id
                )
            )
            
            # Checklist
            st.subheader("Checklist de Saída")
            
            checklist_data = {}
            itens = checklist.get_itens_saida()
            
            for categoria, items in itens.items():
                st.write(f"**{categoria}**")
                for item in items:
                    checklist_data[f"{categoria} - {item}"] = st.checkbox(
                        item,
                        key=f"saida_{categoria}_{item}"
                    )
                st.write("---")
                
            # Observações
            observacoes = st.text_area("Observações")
            
            # Botão de registro
            if st.form_submit_button("Registrar Saída"):
                sucesso, mensagem = registrar_saida(
                    db,
                    condutor_id,
                    veiculo_id,
                    quilometragem,
                    checklist_data,
                    observacoes
                )
                
                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)
                    
    except Exception as e:
        logger.error(f"Erro na página de registro de saída: {str(e)}")
        st.error("Ocorreu um erro ao carregar a página. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 