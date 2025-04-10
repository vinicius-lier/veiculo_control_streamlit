# Sistema de Controle de Veículos

Sistema desenvolvido em Python e Streamlit para controle de entrada e saída de veículos (motos), com gerenciamento de condutores, veículos e registros.

## Funcionalidades

- Autenticação de usuário
- Dashboard com estatísticas
- Cadastro de condutores
- Cadastro de veículos
- Registro de saída de veículos
- Registro de entrada de veículos
- Geração de PDF para registro de saída
- Checklist de saída e entrada
- Histórico de registros

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/controle-veiculos.git
cd controle-veiculos
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Sistema

1. Ative o ambiente virtual (se estiver usando):
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Execute o Streamlit:
```bash
streamlit run app.py
```

3. Acesse o sistema no navegador:
```
http://localhost:8501
```

## Credenciais de Acesso

- Usuário: Vinicius
- Senha: V1n1c1u5@#

## Estrutura do Projeto

```
controle_motos/
├── app.py                 # Página principal e autenticação
├── pages/                 # Páginas do sistema
│   ├── home.py           # Dashboard
│   ├── cadastro_veiculos.py
│   ├── cadastro_condutores.py
│   ├── registrar_saida.py
│   ├── registrar_entrada.py
├── auth/                  # Módulo de autenticação
│   └── login.py
├── utils/                 # Utilitários
│   ├── db.py             # Banco de dados
│   ├── pdf_generator.py  # Geração de PDF
│   ├── checklist.py      # Opções de checklist
├── data/                  # Dados e arquivos
│   ├── veiculos.db       # Banco SQLite
│   ├── arquivos/         # Arquivos gerados
│   │   ├── cnhs/        # CNHs dos condutores
│   │   ├── pdfs/        # PDFs de registro
```

## Banco de Dados

O sistema utiliza SQLite como banco de dados, com as seguintes tabelas:

### condutores
- id (PK)
- nome
- cnh_numero
- cnh_validade
- telefone
- cnh_arquivo

### veiculos
- id (PK)
- marca
- modelo
- placa
- quilometragem_atual
- status

### registros
- id (PK)
- condutor_id (FK)
- veiculo_id (FK)
- data_saida
- data_entrada
- km_saida
- km_entrada
- checklist_saida
- checklist_entrada
- observacoes
- pdf_saida

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 