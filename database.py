import sqlite3
import bcrypt
from datetime import datetime, timedelta
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import json

# Diretório para o banco de dados
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, 'vehicles.db')

def hash_password(password):
    # Gera um salt e faz o hash da senha
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    # Verifica se a senha corresponde ao hash
    return bcrypt.checkpw(password.encode(), hashed)

# Conexão com SQLite
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    db = get_db()
    cursor = db.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        created_at TEXT NOT NULL,
        last_login TEXT
    )
    ''')
    
    # Criar tabela de condutores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        document TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        license_number TEXT NOT NULL,
        license_category TEXT NOT NULL,
        license_expiration TEXT NOT NULL,
        license_photo_path TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT
    )
    ''')
    
    # Criar tabela de veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        color TEXT,
        chassis_number TEXT,
        status TEXT DEFAULT 'available',
        created_at TEXT NOT NULL,
        updated_at TEXT
    )
    ''')
    
    # Criar tabela de saídas de veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_exits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        exit_date TEXT NOT NULL,
        expected_return_date TEXT,
        actual_return_date TEXT,
        initial_odometer INTEGER,
        final_odometer INTEGER,
        destination TEXT,
        purpose TEXT,
        status TEXT NOT NULL DEFAULT 'in_progress',
        external_checklist TEXT,
        internal_checklist TEXT,
        observations TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
        FOREIGN KEY (driver_id) REFERENCES drivers (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Criar tabela de manutenções
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        description TEXT NOT NULL,
        cost REAL,
        date TEXT NOT NULL,
        provider TEXT,
        status TEXT NOT NULL DEFAULT 'scheduled',
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
    )
    ''')
    
    # Criar tabela de abastecimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fuel_consumption (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        liters REAL NOT NULL,
        cost REAL NOT NULL,
        odometer INTEGER NOT NULL,
        gas_station TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
    )
    ''')
    
    # Verificar se existe usuário MASTER
    cursor.execute('SELECT * FROM users WHERE username = ?', ('master',))
    if not cursor.fetchone():
        # Senha: V1n1c1u5@#
        hashed = hash_password('V1n1c1u5@#')
        cursor.execute('''
        INSERT INTO users (username, password, role, name, created_at) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('master', hashed, 'master', 'Administrador Master', datetime.now().isoformat()))
    
    # Verificar se existe usuário Vinicius
    cursor.execute('SELECT * FROM users WHERE username = ?', ('vinicius',))
    if not cursor.fetchone():
        # Senha: V1n1c1u5@#
        hashed = hash_password('V1n1c1u5@#')
        cursor.execute('''
        INSERT INTO users (username, password, role, name, created_at) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('vinicius', hashed, 'user', 'Vinicius', datetime.now().isoformat()))
    
    db.commit()
    db.close()

def create_user(username, password, name, email=None, current_user=None):
    """
    Cria um novo usuário. Apenas o usuário MASTER pode criar novos usuários.
    
    Args:
        username (str): Nome de usuário
        password (str): Senha
        name (str): Nome completo
        email (str, optional): Email
        current_user (dict): Usuário atual que está tentando criar o novo usuário
        
    Returns:
        tuple: (bool, str) - (sucesso, mensagem)
    """
    if not current_user or current_user.get('role') != 'master':
        return False, "Apenas o usuário MASTER pode criar novos usuários"
        
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        db.close()
        return False, "Usuário já existe"
    
    hashed = hash_password(password)
    cursor.execute('''
    INSERT INTO users (username, password, role, name, email, created_at) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, hashed, 'user', name, email, datetime.now().isoformat()))
    
    db.commit()
    db.close()
    return True, "Usuário criado com sucesso"

def verify_user(username, password):
    """Verifica as credenciais do usuário"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        db.close()
        return False, None
    
    if verify_password(password, user['password']):
        # Atualiza o último login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now().isoformat(), user['id']))
        db.commit()
        
        user_dict = dict(user)
        db.close()
        return True, user_dict
    
    db.close()
    return False, None

def register_driver(driver_data):
    """
    Registra um novo condutor no banco de dados.
    
    Args:
        driver_data (dict): Dicionário contendo os dados do condutor
            - name: Nome do condutor
            - document: Número da CNH
            - license_category: Categoria da CNH
            - license_expiration: Data de validade da CNH
            - license_photo_path: Caminho da foto/PDF da CNH (opcional)
            - phone: Telefone (opcional)
            - email: Email (opcional)
            - status: Status do condutor (default: 'active')
    
    Returns:
        int: ID do condutor cadastrado
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO drivers (
                name, document, license_category, license_expiration,
                license_photo_path, phone, email, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            driver_data['nome'],
            driver_data['cnh'],
            driver_data['categoria'],
            driver_data['validade'],
            driver_data.get('foto_cnh'),
            driver_data.get('phone'),
            driver_data.get('email'),
            'active'
        ))
        
        driver_id = cursor.lastrowid
        conn.commit()
        return driver_id
        
    except Exception as e:
        raise Exception(f"Erro ao cadastrar condutor: {str(e)}")
    finally:
        conn.close()

def get_driver(driver_id):
    """Retorna os dados de um condutor"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
    driver = cursor.fetchone()
    db.close()
    
    return dict(driver) if driver else None

def get_drivers():
    """
    Retorna a lista de todos os condutores cadastrados.
    
    Returns:
        list: Lista de dicionários contendo os dados dos condutores
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, document, license_category, license_expiration,
                   license_photo_path, status, created_at, updated_at
            FROM drivers
            ORDER BY name
        """)
        
        drivers = []
        for row in cursor.fetchall():
            drivers.append({
                'id': row[0],
                'nome': row[1],
                'cnh': row[2],
                'categoria': row[3],
                'validade': row[4],
                'foto_cnh': row[5],
                'status': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })
            
        return drivers
        
    except Exception as e:
        raise Exception(f"Erro ao buscar condutores: {str(e)}")
    finally:
        conn.close()

def check_driver_has_active_vehicle(driver_id):
    """Verifica se o condutor tem veículo em uso"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT * FROM vehicle_exits 
    WHERE driver_id = ? AND status = 'in_progress'
    ''', (driver_id,))
    
    has_active = bool(cursor.fetchone())
    db.close()
    return has_active

def register_vehicle(vehicle_data):
    """Registra um novo veículo no banco de dados"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''INSERT INTO vehicles (plate, type, model, year, color, chassis_number, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (vehicle_data['plate'].upper(),
                  vehicle_data['type'],
                  vehicle_data['model'],
                  vehicle_data['year'],
                  vehicle_data.get('color', ''),
                  vehicle_data.get('chassis_number', ''),
                  'available',
                  datetime.now().isoformat()))
        
        vehicle_id = cursor.lastrowid
        conn.commit()
        return vehicle_id, "Veículo cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return None, "Já existe um veículo cadastrado com esta placa."
    except Exception as e:
        return None, f"Erro ao cadastrar veículo: {str(e)}"
    finally:
        conn.close()

def get_all_vehicles():
    """Retorna todos os veículos cadastrados"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vehicles ORDER BY plate")
    vehicles = {row['id']: dict(row) for row in cursor.fetchall()}
    
    conn.close()
    return vehicles

def get_vehicle(vehicle_id):
    """Retorna os dados de um veículo específico"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
    vehicle = dict(cursor.fetchone())
    
    conn.close()
    return vehicle

def register_vehicle_exit(vehicle_id, driver_id, user_id, exit_data):
    """
    Registra a saída de um veículo.
    
    Args:
        vehicle_id (int): ID do veículo
        driver_id (int): ID do condutor
        user_id (int): ID do usuário que registrou a saída
        exit_data (dict): Dicionário com os dados da saída contendo:
            - exit_date: data/hora de saída
            - expected_return_date: data/hora prevista para retorno
            - initial_odometer: quilometragem inicial
            - destination: destino
            - purpose: finalidade
            - external_checklist: lista de verificação externa
            - internal_checklist: lista de verificação interna
            - observations: observações
            - fuel_level: nível de combustível
            
    Returns:
        int: ID do registro de saída criado
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Verificar se o condutor já tem um veículo ativo
        cursor.execute("""
            SELECT v.plate, v.model 
            FROM vehicle_exits ve 
            JOIN vehicles v ON v.id = ve.vehicle_id 
            WHERE ve.driver_id = ? AND ve.status = 'in_progress'
        """, (driver_id,))
        
        active_vehicle = cursor.fetchone()
        if active_vehicle:
            raise Exception(f"Condutor já possui um veículo ativo: {active_vehicle['plate']} - {active_vehicle['model']}")
        
        # Verificar se o veículo está disponível
        cursor.execute("SELECT status FROM vehicles WHERE id = ?", (vehicle_id,))
        vehicle = cursor.fetchone()
        if not vehicle or vehicle['status'] != 'available':
            raise Exception("Veículo não está disponível para saída")
        
        # Insere o registro de saída
        cursor.execute("""
            INSERT INTO vehicle_exits (
                vehicle_id, driver_id, user_id, exit_date, expected_return_date,
                initial_odometer, destination, purpose, external_checklist,
                internal_checklist, observations, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress', datetime('now'))
        """, (
            vehicle_id, driver_id, user_id,
            exit_data['exit_date'], exit_data['expected_return_date'],
            exit_data['initial_odometer'], exit_data['destination'],
            exit_data['purpose'], json.dumps(exit_data['external_checklist']),
            json.dumps(exit_data['internal_checklist']),
            exit_data.get('observations', '')
        ))
        
        exit_id = cursor.lastrowid
        
        # Atualiza o status do veículo
        cursor.execute("""
            UPDATE vehicles 
            SET status = 'in_use', updated_at = datetime('now')
            WHERE id = ?
        """, (vehicle_id,))
        
        conn.commit()
        
        # Gera o documento de inspeção
        generate_checklist_pdf(exit_id, {
            'vehicle_id': vehicle_id,
            'driver_id': driver_id,
            'exit_date': exit_data['exit_date'],
            'initial_odometer': exit_data['initial_odometer'],
            'fuel_level': exit_data.get('fuel_level', 'Não informado'),
            'external_checklist': exit_data['external_checklist'],
            'internal_checklist': exit_data['internal_checklist'],
            'observations': exit_data.get('observations', '')
        })
        
        return exit_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erro ao registrar saída do veículo: {str(e)}")
    finally:
        conn.close()

def generate_checklist_pdf(exit_id, data):
    """
    Gera um PDF com o checklist de saída/retorno do veículo.
    
    Args:
        exit_id (int): ID do registro de saída
        data (dict): Dicionário com os dados do checklist
    """
    # Criar diretório para PDFs se não existir
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    
    # Nome do arquivo
    filename = f'pdfs/checklist_{exit_id}.pdf'
    
    # Criar documento
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    elements.append(Paragraph("Checklist de Inspeção de Veículo", title_style))
    
    # Informações do veículo
    vehicle = get_vehicle_by_id(data['vehicle_id'])
    elements.append(Paragraph(f"Veículo: {vehicle['plate']} - {vehicle['model']} ({vehicle['year']})", styles['Normal']))
    elements.append(Paragraph(f"Data: {data['exit_date']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Informações do motorista
    driver = get_driver(data['driver_id'])
    elements.append(Paragraph("Informações do Motorista:", styles['Heading2']))
    elements.append(Paragraph(f"Nome: {driver['name']}", styles['Normal']))
    elements.append(Paragraph(f"Documento: {driver['document']}", styles['Normal']))
    elements.append(Paragraph(f"Telefone: {driver.get('phone', 'Não informado')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Quilometragem e combustível
    elements.append(Paragraph("Quilometragem e Combustível:", styles['Heading2']))
    if 'is_return' in data:
        elements.append(Paragraph(f"Quilometragem Final: {data['final_odometer']} km", styles['Normal']))
    else:
        elements.append(Paragraph(f"Quilometragem Inicial: {data['initial_odometer']} km", styles['Normal']))
    elements.append(Paragraph(f"Nível de Combustível: {data['fuel_level']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Checklist externo
    elements.append(Paragraph("Checklist Externo:", styles['Heading2']))
    external_data = [['Item', 'Status']]
    for item, value in data['external_checklist'].items():
        if item != 'observacoes_externas':
            external_data.append([item.replace('_', ' ').title(), 'OK' if value else 'NOK'])
    
    external_table = Table(external_data)
    external_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(external_table)
    
    if data['external_checklist'].get('observacoes_externas'):
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Observações Externas:", styles['Heading3']))
        elements.append(Paragraph(data['external_checklist']['observacoes_externas'], styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Checklist interno
    elements.append(Paragraph("Checklist Interno:", styles['Heading2']))
    internal_data = [['Item', 'Status']]
    for item, value in data['internal_checklist'].items():
        if item != 'observacoes_internas':
            internal_data.append([item.replace('_', ' ').title(), 'OK' if value else 'NOK'])
    
    internal_table = Table(internal_data)
    internal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(internal_table)
    
    if data['internal_checklist'].get('observacoes_internas'):
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Observações Internas:", styles['Heading3']))
        elements.append(Paragraph(data['internal_checklist']['observacoes_internas'], styles['Normal']))
    
    # Observações gerais
    if data.get('observations'):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Observações Gerais:", styles['Heading2']))
        elements.append(Paragraph(data['observations'], styles['Normal']))
    
    # Assinatura
    elements.append(Spacer(1, 50))
    elements.append(Paragraph("Assinatura do Motorista:", styles['Heading3']))
    elements.append(Paragraph("_" * 50, styles['Normal']))
    
    # Gerar PDF
    doc.build(elements)
    
    return filename

def get_vehicle_by_id(vehicle_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
        vehicle = cursor.fetchone()
        
        if vehicle:
            return {
                'id': vehicle[0],
                'plate': vehicle[1],
                'type': vehicle[2],
                'model': vehicle[3],
                'year': vehicle[4],
                'color': vehicle[5],
                'chassis_number': vehicle[6],
                'status': vehicle[7]
            }
        return None
    except Exception as e:
        print(f"Erro ao buscar veículo: {str(e)}")
        return None
    finally:
        conn.close()

def get_active_exits():
    """Retorna todas as saídas ativas"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM vehicle_exits WHERE status = ?', ('in_progress',))
    exits = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in exits}

def register_vehicle_return(exit_id, return_data):
    """
    Registra o retorno de um veículo.
    
    Args:
        exit_id (int): ID do registro de saída
        return_data (dict): Dicionário com os dados do retorno contendo:
            - actual_return_date: data/hora efetiva do retorno
            - final_odometer: quilometragem final
            - fuel_level: nível de combustível
            - external_checklist: lista de verificação externa
            - internal_checklist: lista de verificação interna
            - observations: observações do retorno
            - checklist_file: arquivo do checklist de saída
            
    Returns:
        bool: True se o retorno foi registrado com sucesso
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Busca o ID do veículo associado à saída
        cursor.execute("SELECT vehicle_id FROM vehicle_exits WHERE id = ?", (exit_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception("Registro de saída não encontrado")
            
        vehicle_id = result[0]
        
        # Atualiza o registro de saída
        cursor.execute("""
            UPDATE vehicle_exits 
            SET actual_return_date = ?,
                final_odometer = ?,
                external_checklist = ?,
                internal_checklist = ?,
                observations = CASE 
                    WHEN observations IS NULL OR observations = '' 
                    THEN ? 
                    ELSE observations || char(10) || ?
                END,
                status = 'completed',
                updated_at = datetime('now')
            WHERE id = ?
        """, (
            return_data['actual_return_date'],
            return_data['final_odometer'],
            json.dumps(return_data['external_checklist']),
            json.dumps(return_data['internal_checklist']),
            'Observações do retorno: ' + return_data.get('observations', ''),
            'Observações do retorno: ' + return_data.get('observations', ''),
            exit_id
        ))
        
        # Atualiza o status do veículo
        cursor.execute("""
            UPDATE vehicles 
            SET status = 'available',
                updated_at = datetime('now')
            WHERE id = ?
        """, (vehicle_id,))
        
        conn.commit()
        
        # Gera o documento de inspeção de retorno
        generate_checklist_pdf(exit_id, {
            'vehicle_id': vehicle_id,
            'exit_date': return_data['actual_return_date'],
            'final_odometer': return_data['final_odometer'],
            'fuel_level': return_data.get('fuel_level', 'Não informado'),
            'external_checklist': return_data['external_checklist'],
            'internal_checklist': return_data['internal_checklist'],
            'observations': return_data.get('observations', ''),
            'is_return': True
        })
        
        return True
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erro ao registrar retorno do veículo: {str(e)}")
    finally:
        conn.close()

def get_weekly_report():
    """
    Gera um relatório semanal de uso dos veículos.
    
    Returns:
        dict: Dicionário com estatísticas semanais contendo:
            - total_exits: número total de saídas
            - active_exits: número de saídas em andamento
            - completed_exits: número de saídas concluídas
            - vehicles_stats: estatísticas por veículo
            - drivers_stats: estatísticas por motorista
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Define o período (últimos 7 dias)
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # Estatísticas gerais
        cursor.execute("""
            SELECT 
                COUNT(*) as total_exits,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as active_exits,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_exits
            FROM vehicle_exits 
            WHERE exit_date >= ?
        """, (seven_days_ago.isoformat(),))
        
        general_stats = dict(cursor.fetchone())
        
        # Estatísticas por veículo
        cursor.execute("""
            SELECT 
                v.id,
                v.plate,
                v.model,
                COUNT(ve.id) as total_exits,
                SUM(CASE WHEN ve.status = 'in_progress' THEN 1 ELSE 0 END) as active_exits,
                SUM(CASE WHEN ve.status = 'completed' THEN 1 ELSE 0 END) as completed_exits,
                SUM(CASE 
                    WHEN ve.status = 'completed' AND ve.final_odometer IS NOT NULL 
                    THEN ve.final_odometer - ve.initial_odometer 
                    ELSE 0 
                END) as total_km
            FROM vehicles v
            LEFT JOIN vehicle_exits ve ON v.id = ve.vehicle_id 
                AND ve.exit_date >= ?
            GROUP BY v.id, v.plate, v.model
            ORDER BY total_exits DESC
        """, (seven_days_ago.isoformat(),))
        
        vehicles_stats = [dict(row) for row in cursor.fetchall()]
        
        # Estatísticas por motorista
        cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.license_category,
                COUNT(ve.id) as total_exits,
                SUM(CASE WHEN ve.status = 'in_progress' THEN 1 ELSE 0 END) as active_exits,
                SUM(CASE WHEN ve.status = 'completed' THEN 1 ELSE 0 END) as completed_exits,
                COUNT(DISTINCT ve.vehicle_id) as different_vehicles
            FROM drivers d
            LEFT JOIN vehicle_exits ve ON d.id = ve.driver_id 
                AND ve.exit_date >= ?
            GROUP BY d.id, d.name, d.license_category
            ORDER BY total_exits DESC
        """, (seven_days_ago.isoformat(),))
        
        drivers_stats = [dict(row) for row in cursor.fetchall()]
        
        return {
            **general_stats,
            'vehicles_stats': vehicles_stats,
            'drivers_stats': drivers_stats
        }
        
    except Exception as e:
        raise Exception(f"Erro ao gerar relatório semanal: {str(e)}")
    finally:
        conn.close()

def get_driver_statistics():
    """Retorna estatísticas dos motoristas"""
    db = get_db()
    cursor = db.cursor()
    
    # Motorista com mais saídas
    cursor.execute('''
    SELECT d.id, d.name, COUNT(*) as total_saidas
    FROM drivers d
    JOIN vehicle_exits v ON d.id = v.driver_id
    GROUP BY d.id, d.name
    ORDER BY total_saidas DESC
    ''')
    most_exits = cursor.fetchall()
    
    # Motorista com maior quilometragem
    cursor.execute('''
    SELECT d.id, d.name, SUM(v.final_odometer - v.initial_odometer) as total_km
    FROM drivers d
    JOIN vehicle_exits v ON d.id = v.driver_id
    WHERE v.final_odometer IS NOT NULL AND v.initial_odometer IS NOT NULL
    GROUP BY d.id, d.name
    ORDER BY total_km DESC
    ''')
    most_km = cursor.fetchall()
    
    # Motorista com maior tempo de uso
    cursor.execute('''
    SELECT d.id, d.name, 
           SUM(CAST((julianday(v.actual_return_date) - julianday(v.exit_date)) * 24 AS INTEGER)) as total_horas
    FROM drivers d
    JOIN vehicle_exits v ON d.id = v.driver_id
    WHERE v.actual_return_date IS NOT NULL
    GROUP BY d.id, d.name
    ORDER BY total_horas DESC
    ''')
    most_time = cursor.fetchall()
    
    db.close()
    
    return {
        'most_exits': [dict(row) for row in most_exits],
        'most_km': [dict(row) for row in most_km],
        'most_time': [dict(row) for row in most_time]
    } 