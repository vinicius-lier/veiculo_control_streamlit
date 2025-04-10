import streamlit as st
import sqlite3
from datetime import datetime
from utils.db import get_connection, verificar_condutor_disponivel, verificar_veiculo_disponivel
from utils.checklist import get_checklist_options
from utils.pdf_generator import gerar_pdf_saida

# Configuração da página
st.set_page_config(
    page_title="Registro de Saída",
    page_icon="🚀",
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("🚀 Registro de Saída de Veículo")

# Função para obter condutores disponíveis
def get_condutores_disponiveis():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, nome, cnh_numero
    FROM condutores
    WHERE id NOT IN (
        SELECT condutor_id
        FROM registros
        WHERE data_entrada IS NULL
    )
    ORDER BY nome
    """)
    
    condutores = cursor.fetchall()
    conn.close()
    return condutores

# Função para obter veículos disponíveis
def get_veiculos_disponiveis():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, marca, modelo, placa, quilometragem_atual
    FROM veiculos
    WHERE status = 'disponivel'
    ORDER BY marca, modelo
    """)
    
    veiculos = cursor.fetchall()
    conn.close()
    return veiculos

# Função para registrar saída
def registrar_saida(condutor_id, veiculo_id, km_saida, checklist_saida, observacoes):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar disponibilidade
        if not verificar_condutor_disponivel(condutor_id):
            return False, "Condutor já possui um veículo em uso."
        
        if not verificar_veiculo_disponivel(veiculo_id):
            return False, "Veículo não está disponível."
        
        # Obter dados para o PDF
        cursor.execute("""
        SELECT c.nome, c.cnh_numero, v.marca, v.modelo, v.placa
        FROM condutores c, veiculos v
        WHERE c.id = ? AND v.id = ?
        """, (condutor_id, veiculo_id))
        
        dados = cursor.fetchone()
        
        # Gerar PDF
        dados_pdf = {
            'condutor': {'nome': dados[0], 'cnh': dados[1]},
            'veiculo': {'marca': dados[2], 'modelo': dados[3], 'placa': dados[4]},
            'km_saida': km_saida,
            'checklist': checklist_saida,
            'observacoes': observacoes
        }
        
        pdf_path = gerar_pdf_saida(dados_pdf)
        
        # Registrar saída
        cursor.execute("""
        INSERT INTO registros (
            condutor_id, veiculo_id, data_saida, km_saida,
            checklist_saida, observacoes, pdf_saida
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (condutor_id, veiculo_id, datetime.now(), km_saida,
              checklist_saida, observacoes, pdf_path))
        
        # Atualizar status do veículo
        cursor.execute("""
        UPDATE veiculos
        SET status = 'em uso'
        WHERE id = ?
        """, (veiculo_id,))
        
        conn.commit()
        return True, "Saída registrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar saída: {str(e)}"
    finally:
        conn.close()

# Obter dados para os selects
condutores = get_condutores_disponiveis()
veiculos = get_veiculos_disponiveis()

if not condutores:
    st.warning("Não há condutores disponíveis para retirada de veículo.")
elif not veiculos:
    st.warning("Não há veículos disponíveis para retirada.")
else:
    # Formulário de registro
    with st.form("registro_saida"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Select de condutores
            condutor_opcoes = {f"{c[1]} (CNH: {c[2]})": c[0] for c in condutores}
            condutor_selecionado = st.selectbox("Selecione o Condutor", options=list(condutor_opcoes.keys()))
            condutor_id = condutor_opcoes[condutor_selecionado]
            
            # Select de veículos
            veiculo_opcoes = {f"{v[1]} {v[2]} - {v[3]} (KM: {v[4]})": v[0] for v in veiculos}
            veiculo_selecionado = st.selectbox("Selecione o Veículo", options=list(veiculo_opcoes.keys()))
            veiculo_id = veiculo_opcoes[veiculo_selecionado]
            
            # Quilometragem
            km_saida = st.number_input("Quilometragem na Saída", min_value=0, step=1)
        
        with col2:
            # Checklist
            st.subheader("Checklist de Saída")
            checklist_opcoes = get_checklist_options('saida')
            checklist_selecionado = []
            
            for categoria, itens in checklist_opcoes.items():
                st.write(f"**{categoria}**")
                for item in itens:
                    if st.checkbox(item, key=f"check_{item}"):
                        checklist_selecionado.append(item)
            
            # Observações
            observacoes = st.text_area("Observações")
        
        submitted = st.form_submit_button("Registrar Saída")
        
        if submitted:
            if not checklist_selecionado:
                st.error("Por favor, preencha o checklist!")
            else:
                checklist_texto = "\n".join(checklist_selecionado)
                sucesso, mensagem = registrar_saida(
                    condutor_id,
                    veiculo_id,
                    km_saida,
                    checklist_texto,
                    observacoes
                )
                
                if sucesso:
                    st.success(mensagem)
                    # Limpar formulário
                    st.experimental_rerun()
                else:
                    st.error(mensagem) 