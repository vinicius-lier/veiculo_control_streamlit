# Sistema de Controle de Veículos

Sistema para controle de veículos desenvolvido com Python e Streamlit.

## Funcionalidades

- Autenticação de usuários
- Dashboard com estatísticas
- Cadastro de condutores
- Cadastro de veículos
- Registro de saída de veículos
- Registro de entrada de veículos
- Geração de PDF para registros
- Checklist de saída e entrada
- Controle de quilometragem

## Requisitos

- Python 3.8+
- SQLite3

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/veiculo-control-streamlit.git
cd veiculo-control-streamlit
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o aplicativo:
```bash
streamlit run app.py
```

2. Acesse no navegador:
```
http://localhost:8501
```

3. Credenciais de acesso:
```
Usuário: admin@admin.com
Senha: Admin@123
```

## Estrutura do Projeto

```
.
├── app.py                  # Arquivo principal
├── pages/                  # Páginas do sistema
│   ├── home.py            # Dashboard
│   ├── cadastro_condutores.py
│   ├── cadastro_veiculos.py
│   ├── registrar_saida.py
│   └── registrar_entrada.py
├── utils/                  # Utilitários
│   ├── auth.py            # Autenticação
│   ├── database.py        # Banco de dados
│   ├── pdf_generator.py   # Geração de PDF
│   ├── checklist.py       # Checklist
│   ├── validators.py      # Validações
│   ├── constants.py       # Constantes
│   └── schema.py          # Esquema do banco
├── data/                   # Dados
│   ├── logs/              # Logs do sistema
│   └── pdfs/              # PDFs gerados
├── requirements.txt        # Dependências
└── README.md              # Documentação
```

## Banco de Dados

### Tabela: usuarios
- id (INTEGER PRIMARY KEY)
- nome (TEXT)
- email (TEXT UNIQUE)
- senha (TEXT)
- data_criacao (TIMESTAMP)

### Tabela: condutores
- id (INTEGER PRIMARY KEY)
- nome (TEXT)
- cnh (TEXT UNIQUE)
- categoria (TEXT)
- validade_cnh (DATE)
- telefone (TEXT)
- email (TEXT)
- data_criacao (TIMESTAMP)
- data_atualizacao (TIMESTAMP)

### Tabela: veiculos
- id (INTEGER PRIMARY KEY)
- marca (TEXT)
- modelo (TEXT)
- ano (INTEGER)
- placa (TEXT UNIQUE)
- quilometragem (INTEGER)
- status (TEXT)
- data_criacao (TIMESTAMP)
- data_atualizacao (TIMESTAMP)

### Tabela: registros
- id (INTEGER PRIMARY KEY)
- condutor_id (INTEGER FOREIGN KEY)
- veiculo_id (INTEGER FOREIGN KEY)
- data_saida (TIMESTAMP)
- km_saida (INTEGER)
- checklist_saida (TEXT)
- observacoes_saida (TEXT)
- data_entrada (TIMESTAMP)
- km_entrada (INTEGER)
- checklist_entrada (TEXT)
- observacoes_entrada (TEXT)

## Contribuição

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 