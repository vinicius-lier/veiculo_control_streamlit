# Sistema de Gestão de Veículos

Sistema web desenvolvido em Streamlit para gerenciamento de veículos, incluindo controle de saídas, retornos e condutores.

## Funcionalidades

- Sistema de autenticação de usuários
- Gerenciamento de condutores
- Registro de saída de veículos
- Registro de retorno de veículos
- Geração de relatórios
- Upload e gerenciamento de imagens de avarias

## Deploy no Render

1. Crie uma nova conta no [Render](https://render.com)
2. Clique em "New +" e selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure o serviço:
   - **Name**: escolha um nome para seu serviço
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py`
   - **Plan**: Free

## Configuração Local

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```

## Estrutura do Projeto

- `app.py`: Aplicativo principal
- `database.py`: Gerenciamento do banco de dados
- `utils.py`: Funções utilitárias
- `pages/`: Módulos específicos para cada funcionalidade
- `imagens/`: Armazenamento de imagens de avarias 