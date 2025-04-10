import streamlit as st
import os
from datetime import datetime
from utils.db import get_connection
import pandas as pd
import sqlite3
import logging
from utils.auth import Auth
from utils.database import Database
from utils.validators import (
    validar_nome,
    validar_cnh,
    validar_data,
    validar_telefone,
    validar_email
)
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
    page_title=f"{TITULO_APP} - Cadastro de Condutores",
    page_icon=ICONE_APP,
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("👤 Cadastro de Condutores")

# Função para salvar o arquivo da CNH
def salvar_arquivo_cnh(uploaded_file):
    if uploaded_file is not None:
        # Criar diretório se não existir
        os.makedirs('data/arquivos/cnhs', exist_ok=True)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(uploaded_file.name)[1]
        filename = f"cnh_{timestamp}{file_extension}"
        
        # Salvar arquivo
        file_path = os.path.join('data/arquivos/cnhs', filename)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    return None

# Função para cadastrar condutor
def cadastrar_condutor(db: Database, dados: dict) -> tuple[bool, str]:
    """
    Cadastra um novo condutor.
    
    Args:
        db: Instância do banco de dados
        dados: Dados do condutor
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Validações
        if not all(dados.values()):
            return False, AVISO_CAMPO_OBRIGATORIO
            
        valido, msg = validar_cnh(dados['cnh'])
        if not valido:
            return False, msg
            
        valido, msg = validar_data(dados['validade_cnh'])
        if not valido:
            return False, msg
            
        valido, msg = validar_telefone(dados['telefone'])
        if not valido:
            return False, msg
            
        valido, msg = validar_email(dados['email'])
        if not valido:
            return False, msg
            
        # Verifica se CNH já existe
        condutor = db.execute_query(
            "SELECT id FROM condutores WHERE cnh = ?",
            (dados['cnh'],)
        )
        if condutor:
            return False, "CNH já cadastrada"
            
        # Insere condutor
        query = """
            INSERT INTO condutores (
                nome, cnh, categoria, validade_cnh, 
                telefone, email
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            dados['nome'],
            dados['cnh'],
            dados['categoria'],
            dados['validade_cnh'],
            dados['telefone'],
            dados['email']
        ))
        
        logger.info(f"Condutor {dados['nome']} cadastrado com sucesso")
        return True, SUCESSO_REGISTRO
        
    except Exception as e:
        logger.error(f"Erro ao cadastrar condutor: {str(e)}")
        return False, str(e)

# Função para atualizar condutor
def atualizar_condutor(db: Database, id: int, dados: dict) -> tuple[bool, str]:
    """
    Atualiza os dados de um condutor.
    
    Args:
        db: Instância do banco de dados
        id: ID do condutor
        dados: Novos dados do condutor
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Validações
        if not all(dados.values()):
            return False, AVISO_CAMPO_OBRIGATORIO
            
        valido, msg = validar_cnh(dados['cnh'])
        if not valido:
            return False, msg
            
        valido, msg = validar_data(dados['validade_cnh'])
        if not valido:
            return False, msg
            
        valido, msg = validar_telefone(dados['telefone'])
        if not valido:
            return False, msg
            
        valido, msg = validar_email(dados['email'])
        if not valido:
            return False, msg
            
        # Verifica se CNH já existe para outro condutor
        condutor = db.execute_query(
            "SELECT id FROM condutores WHERE cnh = ? AND id != ?",
            (dados['cnh'], id)
        )
        if condutor:
            return False, "CNH já cadastrada para outro condutor"
            
        # Atualiza condutor
        query = """
            UPDATE condutores 
            SET nome = ?, cnh = ?, categoria = ?, 
                validade_cnh = ?, telefone = ?, email = ?
            WHERE id = ?
        """
        db.execute_query(query, (
            dados['nome'],
            dados['cnh'],
            dados['categoria'],
            dados['validade_cnh'],
            dados['telefone'],
            dados['email'],
            id
        ))
        
        logger.info(f"Condutor {dados['nome']} atualizado com sucesso")
        return True, SUCESSO_ATUALIZACAO
        
    except Exception as e:
        logger.error(f"Erro ao atualizar condutor: {str(e)}")
        return False, str(e)

# Função para excluir condutor
def excluir_condutor(db: Database, id: int) -> tuple[bool, str]:
    """
    Exclui um condutor.
    
    Args:
        db: Instância do banco de dados
        id: ID do condutor
        
    Returns:
        Tuple com (bool indicando sucesso, mensagem)
    """
    try:
        # Verifica se condutor tem registros
        registros = db.execute_query(
            "SELECT id FROM registros WHERE condutor_id = ?",
            (id,)
        )
        if registros:
            return False, "Não é possível excluir condutor com registros"
            
        # Exclui condutor
        db.execute_query(
            "DELETE FROM condutores WHERE id = ?",
            (id,)
        )
        
        logger.info(f"Condutor {id} excluído com sucesso")
        return True, SUCESSO_EXCLUSAO
        
    except Exception as e:
        logger.error(f"Erro ao excluir condutor: {str(e)}")
        return False, str(e)

def carregar_condutores(db: Database) -> pd.DataFrame:
    """
    Carrega os condutores cadastrados.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        DataFrame com os condutores
    """
    try:
        condutores = db.execute_query("""
            SELECT 
                id,
                nome,
                cnh,
                categoria,
                validade_cnh,
                telefone,
                email
            FROM condutores
            ORDER BY nome
        """)
        
        return pd.DataFrame(condutores)
    except Exception as e:
        logger.error(f"Erro ao carregar condutores: {str(e)}")
        return pd.DataFrame()

# Formulário de cadastro
with st.form("cadastro_condutor"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome Completo")
        cnh = st.text_input("CNH")
        categoria = st.selectbox("Categoria", ["A", "B", "AB", "C", "D", "E"])
        validade_cnh = st.date_input("Validade da CNH")
    
    with col2:
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
    
    submitted = st.form_submit_button("Cadastrar Condutor")
    
    if submitted:
        if not all([nome, cnh, categoria, validade_cnh, telefone, email]):
            st.error("Por favor, preencha todos os campos!")
        else:
            # Cadastrar condutor
            db = Database()
            sucesso, mensagem = cadastrar_condutor(
                db,
                {
                    'nome': nome,
                    'cnh': cnh,
                    'categoria': categoria,
                    'validade_cnh': validade_cnh.strftime('%Y-%m-%d'),
                    'telefone': telefone,
                    'email': email
                }
            )
            
            if sucesso:
                st.success(mensagem)
                # Limpar formulário
                st.rerun()
            else:
                st.error(mensagem)

# Lista de condutores cadastrados
st.subheader("Condutores Cadastrados")
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT nome, cnh, categoria, validade_cnh, telefone, email
FROM condutores
ORDER BY nome
""")

condutores = cursor.fetchall()
conn.close()

if condutores:
    df = pd.DataFrame(condutores, columns=['Nome', 'CNH', 'Categoria', 'Validade CNH', 'Telefone', 'Email'])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum condutor cadastrado.")

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
        st.title("Cadastro de Condutores")
        
        # Tabs
        tab_lista, tab_cadastro = st.tabs(["Lista de Condutores", "Novo Condutor"])
        
        # Tab Lista
        with tab_lista:
            st.subheader("Condutores Cadastrados")
            
            # Carrega condutores
            df = carregar_condutores(db)
            
            if df.empty:
                st.info("Nenhum condutor cadastrado")
            else:
                # Exibe tabela
                st.dataframe(
                    df,
                    column_config={
                        "id": "ID",
                        "nome": "Nome",
                        "cnh": "CNH",
                        "categoria": "Categoria",
                        "validade_cnh": "Validade CNH",
                        "telefone": "Telefone",
                        "email": "Email"
                    },
                    hide_index=True
                )
                
                # Seleção para edição/exclusão
                col1, col2 = st.columns(2)
                
                with col1:
                    condutor_id = st.selectbox(
                        "Selecione um condutor para editar",
                        df['id'].tolist(),
                        format_func=lambda x: df[df['id'] == x]['nome'].iloc[0]
                    )
                    
                    if st.button("Editar"):
                        condutor = df[df['id'] == condutor_id].iloc[0]
                        st.session_state.editando_condutor = {
                            'id': condutor_id,
                            'nome': condutor['nome'],
                            'cnh': condutor['cnh'],
                            'categoria': condutor['categoria'],
                            'validade_cnh': condutor['validade_cnh'],
                            'telefone': condutor['telefone'],
                            'email': condutor['email']
                        }
                        st.rerun()
                        
                with col2:
                    if st.button("Excluir"):
                        if st.session_state.get('confirmando_exclusao') == condutor_id:
                            sucesso, mensagem = excluir_condutor(db, condutor_id)
                            if sucesso:
                                st.success(mensagem)
                                del st.session_state.confirmando_exclusao
                                st.rerun()
                            else:
                                st.error(mensagem)
                        else:
                            st.session_state.confirmando_exclusao = condutor_id
                            st.warning("Clique novamente para confirmar a exclusão")
                            
        # Tab Cadastro
        with tab_cadastro:
            st.subheader("Novo Condutor" if not st.session_state.get('editando_condutor') else "Editar Condutor")
            
            with st.form("form_condutor"):
                # Campos do formulário
                nome = st.text_input(
                    "Nome",
                    value=st.session_state.get('editando_condutor', {}).get('nome', '')
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    cnh = st.text_input(
                        "CNH",
                        value=st.session_state.get('editando_condutor', {}).get('cnh', '')
                    )
                    
                    categoria = st.selectbox(
                        "Categoria",
                        ["A", "B", "AB", "C", "D", "E"],
                        index=["A", "B", "AB", "C", "D", "E"].index(
                            st.session_state.get('editando_condutor', {}).get('categoria', 'A')
                        )
                    )
                    
                    validade_cnh = st.date_input(
                        "Validade CNH",
                        value=datetime.strptime(
                            st.session_state.get('editando_condutor', {}).get('validade_cnh', datetime.now().strftime('%Y-%m-%d')),
                            '%Y-%m-%d'
                        ).date()
                    )
                    
                with col2:
                    telefone = st.text_input(
                        "Telefone",
                        value=st.session_state.get('editando_condutor', {}).get('telefone', '')
                    )
                    
                    email = st.text_input(
                        "Email",
                        value=st.session_state.get('editando_condutor', {}).get('email', '')
                    )
                    
                # Botões
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Salvar"):
                        dados = {
                            'nome': nome,
                            'cnh': cnh,
                            'categoria': categoria,
                            'validade_cnh': validade_cnh.strftime('%Y-%m-%d'),
                            'telefone': telefone,
                            'email': email
                        }
                        
                        if st.session_state.get('editando_condutor'):
                            sucesso, mensagem = atualizar_condutor(
                                db,
                                st.session_state['editando_condutor']['id'],
                                dados
                            )
                        else:
                            sucesso, mensagem = cadastrar_condutor(
                                db,
                                {
                                    'nome': nome,
                                    'cnh': cnh,
                                    'categoria': categoria,
                                    'validade_cnh': validade_cnh.strftime('%Y-%m-%d'),
                                    'telefone': telefone,
                                    'email': email
                                }
                            )
                            
                        if sucesso:
                            st.success(mensagem)
                            if st.session_state.get('editando_condutor'):
                                del st.session_state.editando_condutor
                            st.rerun()
                        else:
                            st.error(mensagem)
                            
                with col2:
                    if st.session_state.get('editando_condutor'):
                        if st.form_submit_button("Cancelar"):
                            del st.session_state.editando_condutor
                            st.rerun()
                            
    except Exception as e:
        logger.error(f"Erro na página de cadastro de condutores: {str(e)}")
        st.error("Ocorreu um erro ao carregar a página. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 