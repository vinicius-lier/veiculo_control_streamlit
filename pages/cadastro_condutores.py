import streamlit as st
import os
from datetime import datetime
from utils.db import get_connection
import pandas as pd
import sqlite3

# Configuração da página
st.set_page_config(
    page_title="Cadastro de Condutores",
    page_icon="👤",
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
def cadastrar_condutor(nome, cnh_numero, cnh_validade, telefone, cnh_arquivo):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO condutores (nome, cnh_numero, cnh_validade, telefone, cnh_arquivo)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, cnh_numero, cnh_validade, telefone, cnh_arquivo))
        
        conn.commit()
        return True, "Condutor cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Erro: CNH já cadastrada no sistema."
    except Exception as e:
        return False, f"Erro ao cadastrar condutor: {str(e)}"
    finally:
        conn.close()

# Formulário de cadastro
with st.form("cadastro_condutor"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome Completo")
        cnh_numero = st.text_input("Número da CNH")
        cnh_validade = st.date_input("Validade da CNH")
    
    with col2:
        telefone = st.text_input("Telefone")
        cnh_arquivo = st.file_uploader("Upload da CNH", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    submitted = st.form_submit_button("Cadastrar Condutor")
    
    if submitted:
        if not all([nome, cnh_numero, cnh_validade, telefone, cnh_arquivo]):
            st.error("Por favor, preencha todos os campos!")
        else:
            # Salvar arquivo da CNH
            arquivo_path = salvar_arquivo_cnh(cnh_arquivo)
            
            if arquivo_path:
                # Cadastrar condutor
                sucesso, mensagem = cadastrar_condutor(
                    nome,
                    cnh_numero,
                    cnh_validade.strftime('%Y-%m-%d'),
                    telefone,
                    arquivo_path
                )
                
                if sucesso:
                    st.success(mensagem)
                    # Limpar formulário
                    st.experimental_rerun()
                else:
                    st.error(mensagem)
            else:
                st.error("Erro ao salvar arquivo da CNH!")

# Lista de condutores cadastrados
st.subheader("Condutores Cadastrados")
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT nome, cnh_numero, cnh_validade, telefone
FROM condutores
ORDER BY nome
""")

condutores = cursor.fetchall()
conn.close()

if condutores:
    df = pd.DataFrame(condutores, columns=['Nome', 'CNH', 'Validade', 'Telefone'])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum condutor cadastrado.") 