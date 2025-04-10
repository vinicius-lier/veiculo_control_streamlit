import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import get_connection
from utils.checklist import get_checklist_options

# Configuração da página
st.set_page_config(
    page_title="Registro de Entrada",
    page_icon="🔙",
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("🔙 Registro de Entrada de Veículo")

# Função para obter veículos em uso
def get_veiculos_em_uso():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT v.id, v.marca, v.modelo, v.placa, v.quilometragem_atual,
           c.nome as condutor, r.km_saida, r.data_saida
    FROM veiculos v
    JOIN registros r ON v.id = r.veiculo_id
    JOIN condutores c ON r.condutor_id = c.id
    WHERE v.status = 'em uso'
    AND r.data_entrada IS NULL
    ORDER BY v.marca, v.modelo
    """)
    
    veiculos = cursor.fetchall()
    conn.close()
    return veiculos

# Função para registrar entrada
def registrar_entrada(veiculo_id, km_entrada, checklist_entrada, observacoes):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Obter registro de saída
        cursor.execute("""
        SELECT id, km_saida
        FROM registros
        WHERE veiculo_id = ? AND data_entrada IS NULL
        """, (veiculo_id,))
        
        registro = cursor.fetchone()
        if not registro:
            return False, "Registro de saída não encontrado."
        
        registro_id, km_saida = registro
        
        # Validar quilometragem
        if km_entrada < km_saida:
            return False, "Quilometragem de entrada não pode ser menor que a de saída."
        
        # Atualizar registro
        cursor.execute("""
        UPDATE registros
        SET data_entrada = ?,
            km_entrada = ?,
            checklist_entrada = ?,
            observacoes = CASE 
                WHEN observacoes IS NULL THEN ?
                ELSE observacoes || '\n' || ?
            END
        WHERE id = ?
        """, (datetime.now(), km_entrada, checklist_entrada,
              observacoes, observacoes, registro_id))
        
        # Atualizar quilometragem e status do veículo
        cursor.execute("""
        UPDATE veiculos
        SET quilometragem_atual = ?,
            status = 'disponivel'
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
    st.warning("Não há veículos em uso para registrar entrada.")
else:
    # Formulário de registro
    with st.form("registro_entrada"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Select de veículos
            veiculo_opcoes = {
                f"{v[1]} {v[2]} - {v[3]} (KM: {v[4]}) - Condutor: {v[5]}": v[0]
                for v in veiculos
            }
            veiculo_selecionado = st.selectbox(
                "Selecione o Veículo",
                options=list(veiculo_opcoes.keys())
            )
            veiculo_id = veiculo_opcoes[veiculo_selecionado]
            
            # Encontrar veículo selecionado
            veiculo_info = next(v for v in veiculos if v[0] == veiculo_id)
            
            # Mostrar informações do registro
            st.info(f"""
            **Informações do Registro:**
            - Condutor: {veiculo_info[5]}
            - Data de Saída: {veiculo_info[7].strftime('%d/%m/%Y %H:%M')}
            - KM na Saída: {veiculo_info[6]}
            """)
            
            # Quilometragem
            km_entrada = st.number_input(
                "Quilometragem na Entrada",
                min_value=veiculo_info[6],
                step=1
            )
        
        with col2:
            # Checklist
            st.subheader("Checklist de Entrada")
            checklist_opcoes = get_checklist_options('entrada')
            checklist_selecionado = []
            
            for categoria, itens in checklist_opcoes.items():
                st.write(f"**{categoria}**")
                for item in itens:
                    if st.checkbox(item, key=f"check_{item}"):
                        checklist_selecionado.append(item)
            
            # Observações
            observacoes = st.text_area("Observações")
        
        submitted = st.form_submit_button("Registrar Entrada")
        
        if submitted:
            if not checklist_selecionado:
                st.error("Por favor, preencha o checklist!")
            else:
                checklist_texto = "\n".join(checklist_selecionado)
                sucesso, mensagem = registrar_entrada(
                    veiculo_id,
                    km_entrada,
                    checklist_texto,
                    observacoes
                )
                
                if sucesso:
                    st.success(mensagem)
                    # Limpar formulário
                    st.experimental_rerun()
                else:
                    st.error(mensagem) 