import streamlit as st
import pandas as pd
from database import get_weekly_report
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
        records.append({
            "ID": exit_id,
            "Condutor": record["condutor"],
            "Veículo": record["tipo_veiculo"],
            "Data Saída": format_datetime(record["data_saida"]),
            "Odômetro Saída": record["odometro_saida"],
            "Avaria Saída": "Sim" if record["tem_avaria"] else "Não",
            "Status": record["status"],
            "Data Retorno": format_datetime(record["data_retorno"]) if "data_retorno" in record else "-",
            "Odômetro Retorno": record.get("odometro_retorno", "-"),
            "Avaria Retorno": "Sim" if record.get("tem_avaria_retorno", False) else "Não"
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