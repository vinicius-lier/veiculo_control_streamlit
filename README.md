# Sistema de Gestão de Veículos

Sistema para gerenciamento de veículos, condutores e registros de entrada/saída.

## Funcionalidades

- Login com usuário MASTER e controle de acesso
- Cadastro de condutores com CNH (imagem ou PDF)
- Cadastro de veículos
- Registro de entrada e saída de veículos
- Geração de documentos de inspeção
- Verificação de disponibilidade de veículos e condutores
- Relatórios e estatísticas

## Requisitos

- Python 3.8 ou superior
- SQLite3
- Redis (opcional, para cache)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/veiculo_control_streamlit.git
cd veiculo_control_streamlit
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

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=False
```

5. Execute o aplicativo:
```bash
streamlit run app.py
```

## Usuários Padrão

- **MASTER**
  - Usuário: master
  - Senha: V1n1c1u5@#

- **Vinicius**
  - Usuário: vinicius
  - Senha: V1n1c1u5@#

## Estrutura do Projeto

```
veiculo_control_streamlit/
├── app.py                 # Aplicativo principal
├── database.py            # Funções do banco de dados
├── redis_client.py        # Cliente Redis
├── utils.py              # Funções utilitárias
├── requirements.txt      # Dependências
├── assets/              # Arquivos estáticos (logo, etc)
├── pdfs/                # Documentos gerados
└── pages/               # Páginas do aplicativo
    ├── gerenciar_condutores.py
    ├── gerenciar_veiculos.py
    ├── registrar_saida.py
    └── registrar_retorno.py
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 