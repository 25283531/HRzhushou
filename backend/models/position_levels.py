from backend.database.db import get_db_connection

def create_tables():
    """创建职位职级相关的表"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建职级类型表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS level_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                    -- 职级类型名称，如"管理序列"、"专业序列"
        code TEXT NOT NULL UNIQUE,             -- 职级类型编码，如"M"、"P"
        description TEXT,                      -- 描述
        is_active BOOLEAN NOT NULL DEFAULT 1,  -- 是否启用
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建职级表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS position_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id INTEGER NOT NULL,              -- 关联的职级类型ID
        name TEXT NOT NULL,                    -- 职级名称，如"主管"、"部长"
        code TEXT NOT NULL,                    -- 职级编码，如"M1"、"P1"
        level INTEGER NOT NULL,                -- 职级等级，用于排序
        description TEXT,                      -- 描述
        is_active BOOLEAN NOT NULL DEFAULT 1,  -- 是否启用
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (type_id) REFERENCES level_types (id),
        UNIQUE (type_id, code)                 -- 确保同一类型下的编码唯一
    )
    ''')
    
    conn.commit()
    conn.close()

def get_all_level_types():
    """获取所有职级类型"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM level_types ORDER BY created_at')
    types = cursor.fetchall()
    conn.close()
    return types

def create_level_type(data):
    """创建职级类型"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO level_types (name, code, description, is_active)
    VALUES (?, ?, ?, ?)
    ''', (data['name'], data['code'], data.get('description'), data.get('is_active', True)))
    type_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return type_id

def update_level_type(type_id, data):
    """更新职级类型"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE level_types
    SET name = ?, code = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (data['name'], data['code'], data.get('description'), data.get('is_active', True), type_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def delete_level_type(type_id):
    """删除职级类型"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM level_types WHERE id = ?', (type_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_position_levels():
    """获取所有职级"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pl.*, lt.name as type_name, lt.code as type_code
    FROM position_levels pl
    JOIN level_types lt ON pl.type_id = lt.id
    ORDER BY lt.code, pl.level
    ''')
    levels = cursor.fetchall()
    conn.close()
    return levels

def get_position_levels_by_type(type_id):
    """获取指定类型的所有职级"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pl.*, lt.name as type_name, lt.code as type_code
    FROM position_levels pl
    JOIN level_types lt ON pl.type_id = lt.id
    WHERE pl.type_id = ?
    ORDER BY pl.level
    ''', (type_id,))
    levels = cursor.fetchall()
    conn.close()
    return levels

def create_position_level(data):
    """创建职级"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO position_levels (type_id, name, code, level, description, is_active)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['type_id'], data['name'], data['code'], data['level'],
          data.get('description'), data.get('is_active', True)))
    level_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return level_id

def update_position_level(level_id, data):
    """更新职级"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE position_levels
    SET type_id = ?, name = ?, code = ?, level = ?, description = ?, is_active = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (data['type_id'], data['name'], data['code'], data['level'],
          data.get('description'), data.get('is_active', True), level_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def delete_position_level(level_id):
    """删除职级"""
    _, conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM position_levels WHERE id = ?', (level_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success 