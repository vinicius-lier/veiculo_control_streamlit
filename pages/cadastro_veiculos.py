import streamlit as st
import sqlite3
from utils.db import get_connection
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Cadastro de Veículos",
    page_icon="🏍️",
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("🏍️ Cadastro de Veículos")

# Função para cadastrar veículo
def cadastrar_veiculo(marca, modelo, placa, quilometragem):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO veiculos (marca, modelo, placa, quilometragem_atual, status)
        VALUES (?, ?, ?, ?, 'disponivel')
        """, (marca, modelo, placa, quilometragem))
        
        conn.commit()
        return True, "Veículo cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Erro: Placa já cadastrada no sistema."
    except Exception as e:
        return False, f"Erro ao cadastrar veículo: {str(e)}"
    finally:
        conn.close()

# Formulário de cadastro
with st.form("cadastro_veiculo"):
    col1, col2 = st.columns(2)
    
    with col1:
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
    
    with col2:
        placa = st.text_input("Placa").upper()
        quilometragem = st.number_input("Quilometragem Atual", min_value=0, step=1)
    
    submitted = st.form_submit_button("Cadastrar Veículo")
    
    if submitted:
        if not all([marca, modelo, placa, quilometragem is not None]):
            st.error("Por favor, preencha todos os campos!")
        else:
            sucesso, mensagem = cadastrar_veiculo(marca, modelo, placa, quilometragem)
            if sucesso:
                st.success(mensagem)
                # Limpar formulário
                st.rerun()
            else:
                st.error(mensagem)

# Lista de veículos cadastrados
st.subheader("Veículos Cadastrados")
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT marca, modelo, placa, quilometragem_atual, status
FROM veiculos
ORDER BY marca, modelo
""")

veiculos = cursor.fetchall()
conn.close()

if veiculos:
    df = pd.DataFrame(veiculos, columns=['Marca', 'Modelo', 'Placa', 'Quilometragem', 'Status'])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum veículo cadastrado.") 