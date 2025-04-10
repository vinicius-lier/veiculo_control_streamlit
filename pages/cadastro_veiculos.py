import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from utils.auth import Auth
from utils.database import Database
from utils.validators import validar_placa, validar_ano, validar_quilometragem
from utils.constants import (
    TITULO_APP,
    ICONE_APP,
    SUCESSO_REGISTRO,
    SUCESSO_ATUALIZACAO,
    SUCESSO_EXCLUSAO,
    AVISO_CAMPO_OBRIGATORIO
)

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title=f"{TITULO_APP} - Cadastro de Veículos",
    page_icon=ICONE_APP,
    layout="wide"
)

def carregar_veiculos(db: Database) -> pd.DataFrame:
    """
    Carrega os veículos cadastrados.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        DataFrame com os veículos
    """
    try:
        veiculos = db.execute_query("""
            SELECT 
                id,
                marca,
                modelo,
                ano,
                placa,
                quilometragem,
                status
            FROM veiculos
            ORDER BY marca, modelo
        """)
        
        return pd.DataFrame(veiculos)
    except Exception as e:
        logger.error(f"Erro ao carregar veículos: {str(e)}")
        return pd.DataFrame()

def cadastrar_veiculo(db: Database, dados: dict) -> tuple[bool, str]:
    """
    Cadastra um novo veículo.
    
    Args:
        db: Instância do banco de dados
        dados: Dados do veículo
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Validações
        if not all(dados.values()):
            return False, AVISO_CAMPO_OBRIGATORIO
            
        valido, msg = validar_placa(dados['placa'])
        if not valido:
            return False, msg
            
        valido, msg = validar_ano(dados['ano'])
        if not valido:
            return False, msg
            
        valido, msg = validar_quilometragem(dados['quilometragem'])
        if not valido:
            return False, msg
            
        # Verifica se placa já existe
        veiculo = db.execute_query(
            "SELECT id FROM veiculos WHERE placa = ?",
            (dados['placa'],)
        )
        if veiculo:
            return False, "Placa já cadastrada"
            
        # Insere veículo
        query = """
            INSERT INTO veiculos (
                marca, modelo, ano, placa, 
                quilometragem, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            dados['marca'],
            dados['modelo'],
            dados['ano'],
            dados['placa'],
            dados['quilometragem'],
            'disponível'
        ))
        
        logger.info(f"Veículo {dados['placa']} cadastrado com sucesso")
        return True, SUCESSO_REGISTRO
        
    except Exception as e:
        logger.error(f"Erro ao cadastrar veículo: {str(e)}")
        return False, str(e)

def atualizar_veiculo(db: Database, id: int, dados: dict) -> tuple[bool, str]:
    """
    Atualiza os dados de um veículo.
    
    Args:
        db: Instância do banco de dados
        id: ID do veículo
        dados: Novos dados do veículo
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Validações
        if not all(dados.values()):
            return False, AVISO_CAMPO_OBRIGATORIO
            
        valido, msg = validar_placa(dados['placa'])
        if not valido:
            return False, msg
            
        valido, msg = validar_ano(dados['ano'])
        if not valido:
            return False, msg
            
        valido, msg = validar_quilometragem(dados['quilometragem'])
        if not valido:
            return False, msg
            
        # Verifica se placa já existe para outro veículo
        veiculo = db.execute_query(
            "SELECT id FROM veiculos WHERE placa = ? AND id != ?",
            (dados['placa'], id)
        )
        if veiculo:
            return False, "Placa já cadastrada para outro veículo"
            
        # Atualiza veículo
        query = """
            UPDATE veiculos 
            SET marca = ?, modelo = ?, ano = ?, 
                placa = ?, quilometragem = ?
            WHERE id = ?
        """
        db.execute_query(query, (
            dados['marca'],
            dados['modelo'],
            dados['ano'],
            dados['placa'],
            dados['quilometragem'],
            id
        ))
        
        logger.info(f"Veículo {dados['placa']} atualizado com sucesso")
        return True, SUCESSO_ATUALIZACAO
        
    except Exception as e:
        logger.error(f"Erro ao atualizar veículo: {str(e)}")
        return False, str(e)

def excluir_veiculo(db: Database, id: int) -> tuple[bool, str]:
    """
    Exclui um veículo.
    
    Args:
        db: Instância do banco de dados
        id: ID do veículo
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Verifica se veículo tem registros
        registros = db.execute_query(
            "SELECT id FROM registros WHERE veiculo_id = ?",
            (id,)
        )
        if registros:
            return False, "Não é possível excluir veículo com registros"
            
        # Exclui veículo
        db.execute_query(
            "DELETE FROM veiculos WHERE id = ?",
            (id,)
        )
        
        logger.info(f"Veículo {id} excluído com sucesso")
        return True, SUCESSO_EXCLUSAO
        
    except Exception as e:
        logger.error(f"Erro ao excluir veículo: {str(e)}")
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
            
        # Inicializa banco de dados
        db = Database()
        
        # Título
        st.title("Cadastro de Veículos")
        
        # Tabs
        tab_lista, tab_cadastro = st.tabs(["Lista de Veículos", "Novo Veículo"])
        
        # Tab Lista
        with tab_lista:
            st.subheader("Veículos Cadastrados")
            
            # Carrega veículos
            df = carregar_veiculos(db)
            
            if df.empty:
                st.info("Nenhum veículo cadastrado")
            else:
                # Exibe tabela
                st.dataframe(
                    df,
                    column_config={
                        "id": "ID",
                        "marca": "Marca",
                        "modelo": "Modelo",
                        "ano": "Ano",
                        "placa": "Placa",
                        "quilometragem": "Quilometragem",
                        "status": "Status"
                    },
                    hide_index=True
                )
                
                # Seleção para edição/exclusão
                col1, col2 = st.columns(2)
                
                with col1:
                    veiculo_id = st.selectbox(
                        "Selecione um veículo para editar",
                        df['id'].tolist(),
                        format_func=lambda x: f"{df[df['id'] == x]['marca'].iloc[0]} {df[df['id'] == x]['modelo'].iloc[0]} - {df[df['id'] == x]['placa'].iloc[0]}"
                    )
                    
                    if st.button("Editar"):
                        veiculo = df[df['id'] == veiculo_id].iloc[0]
                        st.session_state.editando_veiculo = {
                            'id': veiculo_id,
                            'marca': veiculo['marca'],
                            'modelo': veiculo['modelo'],
                            'ano': veiculo['ano'],
                            'placa': veiculo['placa'],
                            'quilometragem': veiculo['quilometragem']
                        }
                        st.rerun()
                        
                with col2:
                    if st.button("Excluir"):
                        if st.session_state.get('confirmando_exclusao') == veiculo_id:
                            sucesso, mensagem = excluir_veiculo(db, veiculo_id)
                            if sucesso:
                                st.success(mensagem)
                                del st.session_state.confirmando_exclusao
                                st.rerun()
                            else:
                                st.error(mensagem)
                        else:
                            st.session_state.confirmando_exclusao = veiculo_id
                            st.warning("Clique novamente para confirmar a exclusão")
                            
        # Tab Cadastro
        with tab_cadastro:
            st.subheader("Novo Veículo" if not st.session_state.get('editando_veiculo') else "Editar Veículo")
            
            with st.form("form_veiculo"):
                # Campos do formulário
                col1, col2 = st.columns(2)
                
                with col1:
                    marca = st.text_input(
                        "Marca",
                        value=st.session_state.get('editando_veiculo', {}).get('marca', '')
                    )
                    
                    modelo = st.text_input(
                        "Modelo",
                        value=st.session_state.get('editando_veiculo', {}).get('modelo', '')
                    )
                    
                    ano = st.number_input(
                        "Ano",
                        min_value=1900,
                        max_value=datetime.now().year + 1,
                        value=st.session_state.get('editando_veiculo', {}).get('ano', datetime.now().year)
                    )
                    
                with col2:
                    placa = st.text_input(
                        "Placa",
                        value=st.session_state.get('editando_veiculo', {}).get('placa', '')
                    )
                    
                    quilometragem = st.number_input(
                        "Quilometragem",
                        min_value=0,
                        value=st.session_state.get('editando_veiculo', {}).get('quilometragem', 0)
                    )
                    
                # Botões
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Salvar"):
                        dados = {
                            'marca': marca,
                            'modelo': modelo,
                            'ano': ano,
                            'placa': placa,
                            'quilometragem': quilometragem
                        }
                        
                        if st.session_state.get('editando_veiculo'):
                            sucesso, mensagem = atualizar_veiculo(
                                db,
                                st.session_state['editando_veiculo']['id'],
                                dados
                            )
                        else:
                            sucesso, mensagem = cadastrar_veiculo(db, dados)
                            
                        if sucesso:
                            st.success(mensagem)
                            if st.session_state.get('editando_veiculo'):
                                del st.session_state.editando_veiculo
                            st.rerun()
                        else:
                            st.error(mensagem)
                            
                with col2:
                    if st.session_state.get('editando_veiculo'):
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.editando_veiculo
                            st.rerun()
                            
    except Exception as e:
        logger.error(f"Erro na página de cadastro de veículos: {str(e)}")
        st.error("Ocorreu um erro ao carregar a página. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 