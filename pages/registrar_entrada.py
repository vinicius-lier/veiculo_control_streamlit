import streamlit as st
import sqlite3
import logging
import os
from datetime import datetime
from utils.db import get_connection
from utils.checklist import get_checklist_entrada_form

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Registro de Entrada",
    page_icon="🚗",
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("🚗 Registro de Entrada")

# Função para obter veículos em uso
def get_veiculos_em_uso():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT v.id, v.marca, v.modelo, v.placa, r.km_saida, r.id as registro_id
        FROM veiculos v
        JOIN registros r ON v.id = r.veiculo_id
        WHERE r.data_entrada IS NULL
        ORDER BY v.marca, v.modelo
        """)
        
        veiculos = cursor.fetchall()
        logger.info(f"Veículos em uso encontrados: {len(veiculos)}")
        return veiculos
    except Exception as e:
        logger.error(f"Erro ao obter veículos em uso: {str(e)}")
        st.error(f"Erro ao obter veículos em uso: {str(e)}")
        return []
    finally:
        conn.close()

# Função para registrar entrada
def registrar_entrada(registro_id, km_entrada, checklist, observacoes):
    conn = None
    try:
        logger.info(f"Iniciando registro de entrada - Registro ID: {registro_id}")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obter dados do registro
        cursor.execute("""
        SELECT v.id, v.marca, v.modelo, v.placa, r.km_saida
        FROM registros r
        JOIN veiculos v ON r.veiculo_id = v.id
        WHERE r.id = ?
        """, (registro_id,))
        
        registro = cursor.fetchone()
        if not registro:
            logger.error(f"Registro {registro_id} não encontrado")
            return False, "Registro não encontrado."
        
        # Validar quilometragem
        if km_entrada < registro[4]:
            logger.warning(f"Quilometragem de entrada ({km_entrada}) menor que a de saída ({registro[4]})")
            return False, "Quilometragem de entrada não pode ser menor que a quilometragem de saída."
        
        # Atualizar registro
        cursor.execute("""
        UPDATE registros
        SET data_entrada = ?,
            km_entrada = ?,
            checklist_entrada = ?,
            observacoes_entrada = ?
        WHERE id = ?
        """, (
            datetime.now(),
            km_entrada,
            checklist,
            observacoes,
            registro_id
        ))
        
        # Atualizar status do veículo
        cursor.execute("""
        UPDATE veiculos
        SET status = 'disponivel',
            quilometragem = ?
        WHERE id = ?
        """, (km_entrada, registro[0]))
        
        conn.commit()
        logger.info(f"Registro de entrada concluído com sucesso - ID: {registro_id}")
        return True, "Entrada registrada com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao registrar entrada: {str(e)}")
        if conn:
            conn.rollback()
        return False, f"Erro ao registrar entrada: {str(e)}"
    finally:
        if conn:
            conn.close()

# Obter veículos em uso
veiculos = get_veiculos_em_uso()

if not veiculos:
    st.warning("Não há veículos para registro de entrada.")
else:
    # Formulário de registro
    with st.form("registro_entrada"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção do veículo
            veiculo_opcoes = {f"{v[1]} {v[2]} (Placa: {v[3]})": v[5] for v in veiculos}
            veiculo_selecionado = st.selectbox(
                "Selecione o Veículo",
                options=list(veiculo_opcoes.keys())
            )
            registro_id = veiculo_opcoes[veiculo_selecionado]
        
        with col2:
            # Quilometragem
            km_entrada = st.number_input(
                "Quilometragem na Entrada",
                min_value=0,
                step=1
            )
        
        # Checklist
        st.subheader("Checklist de Entrada")
        checklist_items = get_checklist_entrada_form()
        checklist = "\n".join(checklist_items)
        
        # Observações
        observacoes = st.text_area("Observações")
        
        submitted = st.form_submit_button("Registrar Entrada")
        
        if submitted:
            if not checklist_items:
                st.error("Por favor, preencha o checklist!")
            else:
                with st.spinner("Registrando entrada..."):
                    sucesso, mensagem = registrar_entrada(
                        registro_id,
                        km_entrada,
                        checklist,
                        observacoes
                    )
                
                if sucesso:
                    st.success(mensagem)
                    # Limpar formulário
                    st.rerun()
                else:
                    st.error(mensagem) 