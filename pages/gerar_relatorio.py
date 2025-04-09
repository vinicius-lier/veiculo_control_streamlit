import streamlit as st
import pandas as pd
from database import get_weekly_report, get_driver
from utils import check_login, format_datetime
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Relatório Semanal - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Relatório Semanal")

# Buscar dados
data = get_weekly_report()

if not data:
    st.info("Não há registros nos últimos 7 dias.")
else:
    # Preparar dados para o DataFrame
    records = []
    for exit_id, record in data.items():
        # Obter dados do condutor
        driver = get_driver(record["driver_id"])
        driver_name = driver["name"] if driver else "Condutor não encontrado"
        
        records.append({
            "ID": exit_id,
            "Condutor": driver_name,
            "Veículo": record["vehicle_plate"],
            "Destino": record["destination"],
            "Data Saída": format_datetime(record["data_saida"]),
            "Status": record["status"],
            "Data Retorno": format_datetime(record["data_retorno"]) if record["data_retorno"] else "-",
            "Quilometragem": record.get("quilometragem", "-"),
            "Observações": record.get("observations", "-")
        })
    
    # Criar DataFrame
    df = pd.DataFrame(records)
    
    # Exibir tabela
    st.dataframe(df, use_container_width=True)
    
    # Botão de download
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatório')
    
    st.download_button(
        label="Download Excel",
        data=buffer.getvalue(),
        file_name="relatorio_semanal.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) 