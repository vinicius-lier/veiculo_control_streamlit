import streamlit as st
from database import register_vehicle_exit, get_all_vehicles, create_tables
from utils import check_login

# Configuração da página
st.set_page_config(
    page_title="Registrar Saída - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Criar tabelas se não existirem
create_tables()

# Título da página
st.title("Registrar Saída de Veículo")

# Formulário para registro de saída
with st.form("exit_form"):
    # Informações do veículo
    st.write("### Informações do Veículo")
    vehicles = get_all_vehicles()
    available_vehicles = {vid: v for vid, v in vehicles.items() if v['status'] == 'available'}
    
    if not available_vehicles:
        st.error("Não há veículos disponíveis para saída.")
    else:
        vehicle_options = {f"{v['plate']} - {v['model']} ({v['year']})": vid for vid, v in available_vehicles.items()}
        selected_vehicle = st.selectbox("Selecione o Veículo", options=list(vehicle_options.keys()))
        vehicle_id = vehicle_options[selected_vehicle]
        
        # Informações do motorista
        st.write("### Informações do Motorista")
        driver_name = st.text_input("Nome do Motorista")
        driver_document = st.text_input("Documento do Motorista")
        driver_phone = st.text_input("Telefone do Motorista")
        
        # Checklist externo
        st.write("### Checklist Externo")
        external_checklist = {
            "pintura": st.checkbox("Pintura em bom estado"),
            "vidros": st.checkbox("Vidros sem trincas"),
            "pneus": st.checkbox("Pneus em bom estado"),
            "farois": st.checkbox("Faróis funcionando"),
            "parachoque": st.checkbox("Para-choque sem danos"),
            "observacoes_externas": st.text_area("Observações Externas")
        }
        
        # Checklist interno
        st.write("### Checklist Interno")
        internal_checklist = {
            "bancos": st.checkbox("Bancos em bom estado"),
            "painel": st.checkbox("Painel funcionando"),
            "ar_condicionado": st.checkbox("Ar condicionado funcionando"),
            "radio": st.checkbox("Rádio funcionando"),
            "limpeza": st.checkbox("Veículo limpo"),
            "observacoes_internas": st.text_area("Observações Internas")
        }
        
        submit = st.form_submit_button("Registrar Saída")
        
        if submit:
            if not all([driver_name, driver_document, driver_phone]):
                st.error("Todos os campos são obrigatórios")
            else:
                # Preparar dados
                exit_data = {
                    "vehicle_id": vehicle_id,
                    "driver_name": driver_name,
                    "driver_document": driver_document,
                    "driver_phone": driver_phone,
                    "external_checklist": external_checklist,
                    "internal_checklist": internal_checklist
                }
                
                # Registrar saída
                exit_id, message = register_vehicle_exit(exit_data)
                if exit_id:
                    st.success(message)
                    st.info(f"Checklist gerado com sucesso! ID do registro: {exit_id}")
                else:
                    st.error(message) 