import os
import sqlite3
import json
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hrzhushou.db')

def init_db():
    """初始化数据库，创建必要的表结构"""
    # 确保数据目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建员工表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        employee_id TEXT,
        id_card TEXT,
        department TEXT,
        position TEXT,
        entry_date TEXT,
        leave_date TEXT,
        custom_fields TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 创建职位变动记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS position_changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        old_position TEXT,
        new_position TEXT,
        old_salary REAL,
        new_salary REAL,
        effective_date TEXT,
        created_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')
    
    # 创建考勤数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        status TEXT,
        work_hours REAL,
        late_minutes INTEGER,
        early_leave_minutes INTEGER,
        overtime_hours REAL,
        absence_days REAL,
        custom_data TEXT,
        created_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')
    
    # 创建薪资组表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salary_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        formula TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 创建薪酬单项表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salary_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        name TEXT NOT NULL,
        type TEXT,
        amount REAL,
        level INTEGER,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (group_id) REFERENCES salary_groups (id)
    )
    ''')
    
    # 创建社保项表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insurance_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        personal_rate REAL,
        company_rate REAL,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 创建社保组表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insurance_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        base_amount REAL,
        items TEXT,  -- JSON格式存储关联的社保项ID
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 创建薪资记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salary_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month TEXT,
        base_salary REAL,
        actual_salary REAL,
        deductions REAL,
        insurance REAL,
        tax REAL,
        details TEXT,  -- JSON格式存储详细计算数据
        created_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')
    
    # 创建数据备份表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        description TEXT,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn

def dict_factory(cursor, row):
    """将查询结果转换为字典格式"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def execute_query(query, params=(), one=False):
    """执行SQL查询并返回结果"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        else:
            result = cursor.fetchone() if one else cursor.fetchall()
            conn.close()
            return result
    except Exception as e:
        conn.close()
        raise e

def get_current_time():
    """获取当前时间的字符串表示"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')