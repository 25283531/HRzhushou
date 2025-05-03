from backend.database.db import get_db_connection

def create_tables():
    """初始化数据库，创建必要的表结构"""
    try:
        # 获取数据库连接
        _, conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建薪酬项表
        cursor.execute('''
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
        ''')
        
        # 创建匹配规则表
        cursor.execute('''
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
        ''')
        
        # 创建匹配规则和薪酬项的关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rule_salary_items (
            rule_id INTEGER,
            item_id INTEGER,
            FOREIGN KEY (rule_id) REFERENCES matching_rules (id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES salary_items (id) ON DELETE CASCADE,
            PRIMARY KEY (rule_id, item_id)
        )
        ''')
        
        conn.commit()
        return conn
    except Exception as e:
        print(f"\n致命错误: 数据库初始化失败")
        print(f"异常详情: {str(e)}")
        import traceback
        traceback.print_exc()
        print("应用程序将退出...\n")
        import sys
        sys.exit(1)

def get_all_salary_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM salary_items ORDER BY created_at DESC')
    items = cursor.fetchall()
    conn.close()
    return items

def create_salary_item(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO salary_items (name, code, type, description, calculation_formula, is_fixed, default_value)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['code'], data['type'], data['description'],
          data.get('calculation_formula'), data['is_fixed'], data.get('default_value', 0)))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def update_salary_item(item_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE salary_items
    SET name = ?, code = ?, type = ?, description = ?, calculation_formula = ?, is_fixed = ?, default_value = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (data['name'], data['code'], data['type'], data['description'],
          data.get('calculation_formula'), data['is_fixed'], data.get('default_value', 0), item_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_salary_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM salary_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_all_matching_rules():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT r.*, GROUP_CONCAT(rsi.item_id) as salary_items
    FROM matching_rules r
    LEFT JOIN rule_salary_items rsi ON r.id = rsi.rule_id
    GROUP BY r.id
    ORDER BY r.priority DESC, r.created_at DESC
    ''')
    rules = cursor.fetchall()
    conn.close()
    return rules

def create_matching_rule(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO matching_rules (name, description, conditions, priority, is_active)
        VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['description'], data['conditions'],
              data.get('priority', 0), data.get('is_active', True)))
        rule_id = cursor.lastrowid
        
        # 添加关联的薪酬项
        if 'salary_items' in data:
            salary_items = data['salary_items']
            if isinstance(salary_items, str):
                import json
                salary_items = json.loads(salary_items)
            for item_id in salary_items:
                cursor.execute('''
                INSERT INTO rule_salary_items (rule_id, item_id)
                VALUES (?, ?)
                ''', (rule_id, item_id))
        
        conn.commit()
        return rule_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_matching_rule(rule_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        UPDATE matching_rules
        SET name = ?, description = ?, conditions = ?, priority = ?, is_active = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (data['name'], data['description'], data['conditions'],
              data.get('priority', 0), data.get('is_active', True), rule_id))
        
        # 更新关联的薪酬项
        cursor.execute('DELETE FROM rule_salary_items WHERE rule_id = ?', (rule_id,))
        if 'salary_items' in data:
            salary_items = data['salary_items']
            if isinstance(salary_items, str):
                import json
                salary_items = json.loads(salary_items)
            for item_id in salary_items:
                cursor.execute('''
                INSERT INTO rule_salary_items (rule_id, item_id)
                VALUES (?, ?)
                ''', (rule_id, item_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_matching_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM matching_rules WHERE id = ?', (rule_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0 