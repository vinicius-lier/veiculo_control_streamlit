# Status dos veículos
VEICULO_DISPONIVEL = 'disponivel'
VEICULO_EM_USO = 'em_uso'
VEICULO_EM_MANUTENCAO = 'em_manutencao'
VEICULO_INATIVO = 'inativo'

# Status dos condutores
CONDUTOR_DISPONIVEL = 'disponivel'
CONDUTOR_EM_USO = 'em_uso'
CONDUTOR_INATIVO = 'inativo'

# Tipos de usuário
USUARIO_GERENTE = 'gerente'
USUARIO_PADRAO = 'usuario'

# Configurações do sistema
MAX_TENTATIVAS_LOGIN = 3
TEMPO_BLOQUEIO = 30  # minutos
TOKEN_EXPIRY = 8  # horas
TEMPO_EXPIRACAO_SESSAO = 3600  # 1 hora em segundos

# Diretórios
DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_LOGS = os.path.join(DIR_BASE, 'logs')
DIR_PDFS = os.path.join(DIR_BASE, 'pdfs')
DIR_DB = os.path.join(DIR_BASE, 'data')

# Banco de dados
DB_PATH = os.path.join(DIR_DB, 'veiculo_control.db')

# Arquivos
ARQUIVO_DB = os.path.join(DIR_DB, "veiculo_control.db")

# Mensagens de erro
ERRO_LOGIN = 'Usuário ou senha inválidos'
ERRO_BLOQUEIO = 'Conta bloqueada. Tente novamente em {} minutos'
ERRO_PERMISSAO = 'Você não tem permissão para acessar este recurso'
ERRO_SESSAO = 'Sessão expirada. Por favor, faça login novamente'
ERRO_CONEXAO_DB = "Erro ao conectar ao banco de dados"
ERRO_EXECUCAO_QUERY = "Erro ao executar operação no banco de dados"
ERRO_VALIDACAO = "Erro de validação: {}"
ERRO_GERACAO_PDF = "Erro ao gerar PDF: {}"
ERRO_REGISTRO_NAO_ENCONTRADO = "Registro não encontrado"
ERRO_REGISTRO_DUPLICADO = "Registro já existe no sistema"
ERRO_OPERACAO_NAO_PERMITIDA = "Operação não permitida"
ERRO_EXECUCAO_DB = "Erro ao executar operação no banco de dados"
ERRO_FECHAMENTO_DB = "Erro ao fechar conexão com o banco de dados"
ERRO_GERACAO_PDF = "Erro ao gerar PDF"
ERRO_SALVAMENTO_PDF = "Erro ao salvar PDF"
ERRO_CRIACAO_DIRETORIO = "Erro ao criar diretório"
ERRO_SENHA_INVALIDA = "Senha deve ter no mínimo 8 caracteres, uma letra maiúscula, uma minúscula, um número e um caractere especial"
ERRO_EMAIL_INVALIDO = "Email inválido"
ERRO_TELEFONE_INVALIDO = "Telefone inválido"
ERRO_QUILOMETRAGEM_INVALIDA = "Quilometragem inválida"
ERRO_DATA_INVALIDA = "Data inválida"
ERRO_CNH_INVALIDA = "CNH inválida"
ERRO_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"
ERRO_SENHA_INCORRETA = "Senha incorreta"

# Mensagens de sucesso
SUCESSO_LOGIN = 'Login realizado com sucesso'
SUCESSO_LOGOUT = 'Logout realizado com sucesso'
SUCESSO_CADASTRO = 'Cadastro realizado com sucesso'
SUCESSO_ATUALIZACAO = 'Registro atualizado com sucesso'
SUCESSO_EXCLUSAO = 'Registro excluído com sucesso'
SUCESSO_REGISTRO = "Registro realizado com sucesso"
SUCESSO_ENTRADA = "Entrada registrada com sucesso"
SUCESSO_SAIDA = "Saída registrada com sucesso"

# Validações
MIN_QUILOMETRAGEM = 0
MAX_QUILOMETRAGEM = 999999
MIN_CARACTERES_SENHA = 8
MAX_TENTATIVAS_SENHA = 3
KM_MINIMO = 0
KM_MAXIMO = 999999
TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 20
QUILOMETRAGEM_MINIMA = 0
QUILOMETRAGEM_MAXIMA = 999999

# Mensagens de aviso
AVISO_SEM_DADOS = "Nenhum dado encontrado."
AVISO_CAMPOS_OBRIGATORIOS = "Preencha todos os campos obrigatórios."
AVISO_SENHA_INVALIDA = "Senha deve ter no mínimo 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais"
AVISO_EMAIL_INVALIDO = "Email inválido"
AVISO_TELEFONE_INVALIDO = "Telefone inválido"
AVISO_KM_INVALIDA = "Quilometragem inválida. Deve ser maior que 0"
AVISO_DATA_INVALIDA = "Data inválida"
AVISO_CNH_INVALIDA = "CNH inválida. Deve conter 11 dígitos"
AVISO_CAMPO_OBRIGATORIO = "Campo obrigatório"
AVISO_CNH_EXISTENTE = "CNH já cadastrada"
AVISO_VEICULO_EXISTENTE = "Veículo já cadastrado"
AVISO_KM_INVALIDA = "Quilometragem deve ser maior que a anterior"
AVISO_SENHA_INVALIDA = "Senha não atende aos requisitos mínimos"
AVISO_EMAIL_INVALIDO = "Email em formato inválido"
AVISO_TELEFONE_INVALIDO = "Telefone em formato inválido"
AVISO_DATA_INVALIDA = "Data em formato inválido"
AVISO_CNH_INVALIDA = "CNH em formato inválido"

# Configurações
TITULO_APP = "Controle de Veículos"
ICONE_APP = "🚗"
TEMA_APP = "light" 