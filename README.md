# Sistema de Controle de Veículos

Sistema web desenvolvido em Streamlit para gerenciamento de frota de veículos, incluindo controle de saídas, manutenções e consumo de combustível.

## Funcionalidades

- **Gestão de Usuários**
  - Login e registro de usuários
  - Controle de acesso por perfil

- **Gestão de Veículos**
  - Cadastro de veículos
  - Controle de status
  - Histórico de manutenções

- **Gestão de Motoristas**
  - Cadastro de motoristas
  - Controle de documentação
  - Histórico de saídas

- **Controle de Saídas**
  - Registro de saída e retorno
  - Checklist interno e externo
  - Controle de quilometragem

- **Manutenções**
  - Registro de manutenções preventivas e corretivas
  - Controle de custos
  - Histórico por veículo

- **Combustível**
  - Registro de abastecimentos
  - Controle de consumo
  - Histórico por veículo

- **Relatórios**
  - Relatórios semanais
  - Estatísticas de uso
  - Análise de custos

## Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python
- **Banco de Dados**: SQLite
- **Cache**: Redis
- **Visualização**: Plotly
- **PDF**: ReportLab

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/veiculo_control_streamlit.git
cd veiculo_control_streamlit
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Execute o aplicativo:
```bash
streamlit run app.py
```

## Estrutura do Projeto

```
veiculo_control_streamlit/
├── app.py              # Aplicativo principal
├── database.py         # Funções de banco de dados
├── redis_client.py     # Cliente Redis
├── utils.py           # Funções utilitárias
├── requirements.txt   # Dependências
└── README.md         # Documentação
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 