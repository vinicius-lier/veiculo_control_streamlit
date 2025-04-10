import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import get_connection
from utils.checklist import get_checklist_entrada_form

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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT v.id, v.marca, v.modelo, v.placa, v.quilometragem_atual,
           c.nome, c.cnh_numero, r.data_saida, r.id as registro_id
    FROM veiculos v
    JOIN registros r ON v.id = r.veiculo_id
    JOIN condutores c ON r.condutor_id = c.id
    WHERE r.data_entrada IS NULL
    ORDER BY v.marca, v.modelo
    """)
    
    veiculos = cursor.fetchall()
    conn.close()
    
    return veiculos

# Função para registrar entrada
def registrar_entrada(registro_id, km_entrada, checklist, observacoes):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obter registro atual
        cursor.execute("""
        SELECT veiculo_id, km_saida
        FROM registros
        WHERE id = ?
        """, (registro_id,))
        
        registro = cursor.fetchone()
        veiculo_id = registro[0]
        km_saida = registro[1]
        
        # Validar quilometragem
        if km_entrada < km_saida:
            return False, "A quilometragem de entrada não pode ser menor que a quilometragem de saída."
        
        # Atualizar registro
        cursor.execute("""
        UPDATE registros
        SET data_entrada = ?, km_entrada = ?, checklist_entrada = ?, observacoes = ?
        WHERE id = ?
        """, (datetime.now(), km_entrada, checklist, observacoes, registro_id))
        
        # Atualizar quilometragem do veículo
        cursor.execute("""
        UPDATE veiculos
        SET quilometragem_atual = ?, status = 'disponivel'
        WHERE id = ?
        """, (km_entrada, veiculo_id))
        
        conn.commit()
        return True, "Entrada registrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar entrada: {str(e)}"
    finally:
        conn.close()

# Obter veículos em uso
veiculos = get_veiculos_em_uso()

if not veiculos:
    st.warning("Não há veículos em uso para registro de entrada.")
else:
    # Formulário de registro
    with st.form("registro_entrada"):
        # Seleção do veículo
        veiculo_opcoes = {f"{v[1]} {v[2]} (Placa: {v[3]}) - Condutor: {v[5]}": v[0] for v in veiculos}
        veiculo_selecionado = st.selectbox(
            "Selecione o Veículo",
            options=list(veiculo_opcoes.keys())
        )
        registro_id = veiculo_opcoes[veiculo_selecionado]
        
        # Obter informações do veículo selecionado
        veiculo_info = next(v for v in veiculos if v[0] == registro_id)
        
        # Exibir informações do registro
        st.subheader("Informações do Registro")
        st.write(f"""
        - Veículo: {veiculo_info[1]} {veiculo_info[2]} (Placa: {veiculo_info[3]})
        - Condutor: {veiculo_info[5]} (CNH: {veiculo_info[6]})
        - Quilometragem na Saída: {veiculo_info[4]} km
        - Data de Saída: {veiculo_info[7]}
        """)
        
        # Quilometragem
        km_entrada = st.number_input(
            "Quilometragem na Entrada",
            min_value=veiculo_info[4],
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