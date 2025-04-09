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
    
    # Verificar se existe usuário admin
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Senha padrão: admin123
        hashed = hash_password('admin123')
        cursor.execute('''
        INSERT INTO users (username, password, role, name, created_at) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed, 'admin', 'Administrador', datetime.now().isoformat()))
    
    db.commit()
    db.close()

def create_user(username, password, name, email=None):
    """Cria um novo usuário"""
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
    """Registra um novo condutor"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
    INSERT INTO drivers (name, document, phone, email, license_number, license_category, license_expiration, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (driver_data['nome'], driver_data['cnh'], 
          driver_data.get('telefone', ''), driver_data.get('email', ''),
          driver_data['cnh'], driver_data['categoria'],
          driver_data['validade'], 'ativo', datetime.now().isoformat()))
    
    driver_id = cursor.lastrowid
    db.commit()
    db.close()
    return driver_id

def get_driver(driver_id):
    """Retorna os dados de um condutor"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
    driver = cursor.fetchone()
    db.close()
    
    return dict(driver) if driver else None

def get_all_drivers():
    """Retorna todos os condutores"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM drivers')
    drivers = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in drivers}

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

def register_vehicle_exit(data):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Registrar saída
        cursor.execute('''
            INSERT INTO vehicle_exits (
                vehicle_id, driver_id, user_id, exit_date, expected_return_date,
                initial_odometer, destination, purpose, status, external_checklist, 
                internal_checklist, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['vehicle_id'],
            data['driver_id'],
            data['user_id'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('expected_return_date', ''),
            data.get('initial_odometer', 0),
            data.get('destination', ''),
            data.get('purpose', ''),
            'in_progress',
            json.dumps(data['external_checklist']),
            json.dumps(data['internal_checklist']),
            datetime.now().isoformat()
        ))
        
        exit_id = cursor.lastrowid
        
        # Atualizar status do veículo
        cursor.execute('''
            UPDATE vehicles 
            SET status = 'in_use', updated_at = ? 
            WHERE id = ?
        ''', (datetime.now().isoformat(), data['vehicle_id']))
        
        conn.commit()
        
        # Gerar PDF do checklist
        generate_checklist_pdf(exit_id, data)
        
        return exit_id, "Saída registrada com sucesso!"
    except Exception as e:
        return None, f"Erro ao registrar saída: {str(e)}"
    finally:
        conn.close()

def generate_checklist_pdf(exit_id, data):
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
    elements.append(Paragraph("Checklist de Saída de Veículo", title_style))
    
    # Informações do veículo
    vehicle = get_vehicle_by_id(data['vehicle_id'])
    elements.append(Paragraph(f"Veículo: {vehicle['plate']} - {vehicle['model']} ({vehicle['year']})", styles['Normal']))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Informações do motorista
    driver = get_driver(data['driver_id'])
    elements.append(Paragraph("Informações do Motorista:", styles['Heading2']))
    elements.append(Paragraph(f"Nome: {driver['name']}", styles['Normal']))
    elements.append(Paragraph(f"Documento: {driver['document']}", styles['Normal']))
    elements.append(Paragraph(f"Telefone: {driver.get('phone', 'Não informado')}", styles['Normal']))
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

def register_vehicle_return(exit_id, data):
    """Registra o retorno de um veículo"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM vehicle_exits WHERE id = ?', (exit_id,))
    exit_data = cursor.fetchone()
    
    if not exit_data:
        db.close()
        return False, "Saída não encontrada"
    
    if exit_data['status'] != 'in_progress':
        db.close()
        return False, "Veículo já retornado"
    
    cursor.execute('''
    UPDATE vehicle_exits 
    SET status = ?, actual_return_date = ?, final_odometer = ?, observations = ?, updated_at = ?
    WHERE id = ?
    ''', ('completed', datetime.now().isoformat(), 
          data.get('final_odometer', 0), data.get('observations', ''), 
          datetime.now().isoformat(), exit_id))
    
    # Atualizar status do veículo
    cursor.execute('''
    UPDATE vehicles 
    SET status = 'available', updated_at = ? 
    WHERE id = ?
    ''', (datetime.now().isoformat(), exit_data['vehicle_id']))
    
    db.commit()
    db.close()
    return True, "Retorno registrado com sucesso"

def get_weekly_report():
    """Retorna os registros dos últimos 7 dias"""
    db = get_db()
    cursor = db.cursor()
    
    seven_days_ago = (datetime.now().timestamp() - (7 * 24 * 60 * 60))
    cursor.execute('''
    SELECT * FROM vehicle_exits 
    WHERE datetime(exit_date) > datetime(?)
    ''', (datetime.fromtimestamp(seven_days_ago).isoformat(),))
    
    exits = cursor.fetchall()
    db.close()
    
    return {row['id']: dict(row) for row in exits}

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