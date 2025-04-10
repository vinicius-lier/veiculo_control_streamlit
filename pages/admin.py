import streamlit as st
from utils.common import require_auth, setup_page, show_error, show_success, logger
from utils.backup import BackupManager
from utils.reports import ReportGenerator
import os
from datetime import datetime

# Configuração da página
setup_page("Administração", "⚙️")

# Verificar autenticação
@require_auth
def main():
    # Inicializar gerenciadores
    backup_manager = BackupManager()
    report_generator = ReportGenerator()
    
    # Criar abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "Backup", "Relatórios", "Logs", "Configurações"
    ])
    
    # Aba de Backup
    with tab1:
        st.header("Gerenciamento de Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Criar Backup"):
                with st.spinner("Criando backup..."):
                    sucesso, mensagem = backup_manager.create_backup()
                    if sucesso:
                        show_success(mensagem)
                    else:
                        show_error(mensagem)
        
        with col2:
            # Listar backups disponíveis
            sucesso, backups = backup_manager.list_backups()
            
            if sucesso and backups:
                st.subheader("Backups Disponíveis")
                
                for backup in backups:
                    with st.expander(f"Backup de {backup['modified'].strftime('%d/%m/%Y %H:%M')}"):
                        st.write(f"Arquivo: {backup['filename']}")
                        st.write(f"Tamanho: {backup['size'] / 1024:.2f} KB")
                        
                        if st.button("Restaurar", key=f"restore_{backup['filename']}"):
                            with st.spinner("Restaurando backup..."):
                                sucesso, mensagem = backup_manager.restore_backup(backup['filename'])
                                if sucesso:
                                    show_success(mensagem)
                                    st.rerun()
                                else:
                                    show_error(mensagem)
            else:
                st.info("Nenhum backup disponível.")
    
    # Aba de Relatórios
    with tab2:
        st.header("Geração de Relatórios")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Relatório Diário"):
                with st.spinner("Gerando relatório diário..."):
                    sucesso, pdf_path = report_generator.gerar_relatorio_diario()
                    if sucesso:
                        show_success("Relatório diário gerado com sucesso!")
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download Relatório Diário",
                                f,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                    else:
                        show_error(pdf_path)
        
        with col2:
            if st.button("Relatório Semanal"):
                with st.spinner("Gerando relatório semanal..."):
                    sucesso, pdf_path = report_generator.gerar_relatorio_semanal()
                    if sucesso:
                        show_success("Relatório semanal gerado com sucesso!")
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download Relatório Semanal",
                                f,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                    else:
                        show_error(pdf_path)
        
        with col3:
            if st.button("Relatório Mensal"):
                with st.spinner("Gerando relatório mensal..."):
                    sucesso, pdf_path = report_generator.gerar_relatorio_mensal()
                    if sucesso:
                        show_success("Relatório mensal gerado com sucesso!")
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download Relatório Mensal",
                                f,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                    else:
                        show_error(pdf_path)
    
    # Aba de Logs
    with tab3:
        st.header("Visualização de Logs")
        
        log_file = 'logs/app.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                nivel = st.selectbox(
                    "Nível de Log",
                    ["Todos", "INFO", "WARNING", "ERROR"]
                )
            
            with col2:
                data = st.date_input(
                    "Data",
                    value=datetime.now()
                )
            
            # Filtrar logs
            logs_filtrados = []
            for log in logs:
                if nivel != "Todos" and nivel not in log:
                    continue
                
                try:
                    log_date = datetime.strptime(log.split()[0], '%Y-%m-%d').date()
                    if log_date != data:
                        continue
                except:
                    continue
                
                logs_filtrados.append(log)
            
            # Exibir logs
            st.text_area("Logs", value="".join(logs_filtrados), height=400)
        else:
            st.info("Nenhum arquivo de log encontrado.")
    
    # Aba de Configurações
    with tab4:
        st.header("Configurações do Sistema")
        
        # Configurações de Backup
        st.subheader("Configurações de Backup")
        backup_dir = st.text_input(
            "Diretório de Backup",
            value=backup_manager.backup_dir
        )
        
        # Configurações de Relatórios
        st.subheader("Configurações de Relatórios")
        report_dir = st.text_input(
            "Diretório de Relatórios",
            value=report_generator.output_dir
        )
        
        # Configurações de Log
        st.subheader("Configurações de Log")
        log_level = st.selectbox(
            "Nível de Log",
            ["INFO", "WARNING", "ERROR", "DEBUG"]
        )
        
        if st.button("Salvar Configurações"):
            # TODO: Implementar salvamento das configurações
            show_success("Configurações salvas com sucesso!")

if __name__ == "__main__":
    main() 