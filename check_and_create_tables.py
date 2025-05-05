import os
import sqlite3
import sys

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'data', 'hrzhushou.db')

# 确保数据目录存在
data_dir = os.path.dirname(DATABASE_PATH)
if not os.path.exists(data_dir):
    print(f"创建数据目录: {data_dir}")
    os.makedirs(data_dir, exist_ok=True)

# 连接数据库
print(f"连接数据库: {DATABASE_PATH}")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 获取现有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
existing_tables = [table[0] for table in cursor.fetchall()]
print("现有数据表:")
for table in existing_tables:
    print(f"- {table}")

# 定义预期的表
expected_tables = {
    'salary_items': '''
        CREATE TABLE IF NOT EXISTS salary_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            description TEXT,
            calculation_formula TEXT,
            is_fixed BOOLEAN NOT NULL DEFAULT 1,
            default_value REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'matching_rules': '''
        CREATE TABLE IF NOT EXISTS matching_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            conditions TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'rule_salary_items': '''
        CREATE TABLE IF NOT EXISTS rule_salary_items (
            rule_id INTEGER,
            item_id INTEGER,
            FOREIGN KEY (rule_id) REFERENCES matching_rules (id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES salary_items (id) ON DELETE CASCADE,
            PRIMARY KEY (rule_id, item_id)
        )
    ''',
    
    'attendance': '''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            name TEXT,
            employee_number TEXT,
            id_card TEXT,
            month TEXT,
            should_attend_days REAL DEFAULT 0,
            actual_attend_days REAL DEFAULT 0,
            late_count INTEGER DEFAULT 0,
            serious_late_count INTEGER DEFAULT 0,
            early_leave_count INTEGER DEFAULT 0,
            serious_early_leave_count INTEGER DEFAULT 0,
            absenteeism_count INTEGER DEFAULT 0,
            sick_leave_days REAL DEFAULT 0,
            personal_leave_days REAL DEFAULT 0,
            work_injury_leave_days REAL DEFAULT 0,
            annual_leave_days REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            date DATE NOT NULL,
            status TEXT DEFAULT 'normal',
            work_hours REAL DEFAULT 0,
            late_minutes INTEGER DEFAULT 0,
            early_leave_minutes INTEGER DEFAULT 0,
            absence_days REAL DEFAULT 0,
            custom_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'employees': '''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT NOT NULL UNIQUE,
            id_card TEXT,
            department TEXT,
            position TEXT,
            entry_date DATE,
            leave_date DATE,
            insurance_group_id INTEGER,
            custom_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'position_changes': '''
        CREATE TABLE IF NOT EXISTS position_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            old_position TEXT,
            new_position TEXT,
            old_salary REAL,
            new_salary REAL,
            effective_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
        )
    ''',
    
    'level_types': '''
        CREATE TABLE IF NOT EXISTS level_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'position_levels': '''
        CREATE TABLE IF NOT EXISTS position_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            level INTEGER NOT NULL,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (type_id) REFERENCES level_types (id),
            UNIQUE (type_id, code)
        )
    ''',
    
    'insurance_items': '''
        CREATE TABLE IF NOT EXISTS insurance_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            personal_rate REAL NOT NULL DEFAULT 0,
            company_rate REAL NOT NULL DEFAULT 0,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'insurance_groups': '''
        CREATE TABLE IF NOT EXISTS insurance_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            base_amount REAL NOT NULL DEFAULT 0,
            items TEXT,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
}

# 检查缺失的表并创建
missing_tables = [table for table in expected_tables.keys() if table not in existing_tables]
print("\n缺失的数据表:")
if missing_tables:
    for table in missing_tables:
        print(f"- 创建表: {table}")
        cursor.execute(expected_tables[table])
    conn.commit()
    print("\n所有缺失的表已创建完成")
else:
    print("- 没有缺失的表")

# 关闭连接
conn.close()
print("\n数据库检查完成")