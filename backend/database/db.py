import os
import sqlite3
import json
import threading
import logging
from datetime import datetime
from queue import Queue
from typing import Dict, List, Optional, Tuple, Any

# 配置日志
logger = logging.getLogger('hrzhushou.database')

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hrzhushou.db')

def init_db():
    """初始化数据库，创建必要的表结构"""
    try:
        # 确保数据目录存在
        data_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(data_dir):
            print(f"创建数据目录: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
        
        # 尝试获取数据库连接
        print(f"连接数据库: {DATABASE_PATH}")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("正在初始化数据库...")
        
        # 创建薪酬单项表
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
        print("数据库初始化完成")
        return conn
    except Exception as e:
        print(f"\n致命错误: 数据库初始化失败")
        print(f"异常详情: {str(e)}")
        import traceback
        traceback.print_exc()
        print("应用程序将退出...\n")
        import sys
        sys.exit(1)

# 数据库连接池
class ConnectionPool:
    """简单的数据库连接池实现"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConnectionPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.pool = Queue(maxsize=10)  # 最大连接数
        self.size = 0
        self.active_connections = {}
        self.lock = threading.Lock()
        self.connection_id = 0
        logger.info("数据库连接池已初始化")
    
    def get_connection(self):
        """从连接池获取连接，如果池为空且未达到最大连接数则创建新连接"""
        conn = None
        conn_id = None
        
        try:
            # 尝试从池中获取连接
            if not self.pool.empty():
                conn_id, conn = self.pool.get(block=False)
                logger.debug(f"从连接池获取连接 ID: {conn_id}")
            else:
                # 如果池为空，创建新连接
                with self.lock:
                    if self.size < self.pool.maxsize:
                        conn = self._create_connection()
                        self.size += 1
                        self.connection_id += 1
                        conn_id = self.connection_id
                        logger.debug(f"创建新连接 ID: {conn_id}, 当前连接数: {self.size}")
                    else:
                        # 如果达到最大连接数，等待连接释放
                        logger.warning("已达到最大连接数，等待连接释放")
                        conn_id, conn = self.pool.get(block=True, timeout=30)
                        logger.debug(f"等待后获取连接 ID: {conn_id}")
            
            # 记录活动连接
            if conn and conn_id:
                with self.lock:
                    self.active_connections[conn_id] = {
                        'connection': conn,
                        'thread_id': threading.get_ident(),
                        'timestamp': datetime.now()
                    }
            
            return conn_id, conn
        except Exception as e:
            logger.error(f"获取数据库连接失败: {str(e)}")
            if conn and not self._check_connection(conn):
                # 如果连接无效，创建新连接
                conn = self._create_connection()
                with self.lock:
                    self.connection_id += 1
                    conn_id = self.connection_id
                    self.active_connections[conn_id] = {
                        'connection': conn,
                        'thread_id': threading.get_ident(),
                        'timestamp': datetime.now()
                    }
            return conn_id, conn
    
    def release_connection(self, conn_id, conn):
        """释放连接回连接池"""
        if not conn:
            return
            
        try:
            # 检查连接是否有效
            if self._check_connection(conn):
                # 将连接放回池中
                self.pool.put((conn_id, conn), block=False)
                logger.debug(f"连接 ID: {conn_id} 已释放回连接池")
            else:
                # 如果连接无效，关闭并减少计数
                with self.lock:
                    self.size -= 1
                    logger.debug(f"关闭无效连接 ID: {conn_id}, 当前连接数: {self.size}")
                try:
                    conn.close()
                except Exception:
                    pass
            
            # 从活动连接中移除
            with self.lock:
                if conn_id in self.active_connections:
                    del self.active_connections[conn_id]
        except Exception as e:
            logger.error(f"释放连接失败: {str(e)}")
            # 如果无法放回池中，关闭连接
            try:
                conn.close()
                with self.lock:
                    self.size -= 1
                    if conn_id in self.active_connections:
                        del self.active_connections[conn_id]
                    logger.debug(f"关闭连接 ID: {conn_id}, 当前连接数: {self.size}")
            except Exception:
                pass
    
    def _create_connection(self):
        """创建新的数据库连接"""
        try:
            conn = sqlite3.connect(DATABASE_PATH, timeout=20, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"创建数据库连接失败: {str(e)}")
            raise e
    
    def _check_connection(self, conn):
        """检查连接是否有效"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def close_all(self):
        """关闭所有连接"""
        logger.info("关闭所有数据库连接")
        # 关闭活动连接
        with self.lock:
            for conn_id, conn_info in list(self.active_connections.items()):
                try:
                    conn_info['connection'].close()
                    logger.debug(f"关闭活动连接 ID: {conn_id}")
                except Exception as e:
                    logger.error(f"关闭连接 {conn_id} 失败: {str(e)}")
            self.active_connections.clear()
            
            # 清空连接池
            while not self.pool.empty():
                try:
                    conn_id, conn = self.pool.get(block=False)
                    conn.close()
                    logger.debug(f"关闭池中连接 ID: {conn_id}")
                except Exception:
                    pass
            
            self.size = 0
            logger.info("所有数据库连接已关闭")
    
    def get_stats(self):
        """获取连接池统计信息"""
        with self.lock:
            return {
                'pool_size': self.size,
                'active_connections': len(self.active_connections),
                'available_connections': self.pool.qsize(),
                'max_connections': self.pool.maxsize
            }
    
    def check_for_leaks(self, timeout_seconds=300):
        """检查连接泄漏"""
        leaks = []
        current_time = datetime.now()
        
        with self.lock:
            for conn_id, conn_info in self.active_connections.items():
                duration = (current_time - conn_info['timestamp']).total_seconds()
                if duration > timeout_seconds:
                    leaks.append({
                        'connection_id': conn_id,
                        'thread_id': conn_info['thread_id'],
                        'duration_seconds': duration
                    })
        
        if leaks:
            logger.warning(f"检测到 {len(leaks)} 个可能的连接泄漏: {leaks}")
        
        return leaks

# 全局连接池实例
_connection_pool = None

def get_connection_pool():
    """获取连接池实例"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=20)
        conn.row_factory = dict_factory
        return None, conn
    except sqlite3.Error as e:
        logger.error(f"数据库连接错误: {str(e)}")
        raise e

def get_connection_from_pool():
    return get_db_connection()

def return_connection_to_pool(conn_id, conn):
    """释放数据库连接（兼容旧调用）"""
    pool = get_connection_pool()
    pool.release_connection(conn_id, conn)

def dict_factory(cursor, row):
    """将查询结果转换为字典格式"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def execute_query(query, params=(), one=False):
    """执行SQL查询并返回结果"""
    conn = None
    conn_id = None
    try:
        conn_id, conn = get_connection_from_pool()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
            last_id = cursor.lastrowid
            result = last_id
        else:
            result = cursor.fetchone() if one else cursor.fetchall()
        
        return result
    except Exception as e:
        # 如果发生异常，回滚事务
        if conn and query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            try:
                conn.rollback()
            except Exception as rollback_error:
                print(f"回滚事务时出错: {str(rollback_error)}")
        raise e
    finally:
        # 确保在函数结束时释放数据库连接
        if conn_id is not None and conn is not None:
            try:
                return_connection_to_pool(conn_id, conn)
            except Exception as close_error:
                print(f"释放数据库连接时出错: {str(close_error)}")
                # 不抛出异常，避免掩盖原始错误

def get_current_time():
    """获取当前时间的字符串表示"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def close_all_connections():
    """关闭所有数据库连接，应用退出时调用"""
    try:
        pool = get_connection_pool()
        pool.close_all()
        logger.info("已关闭所有数据库连接")
        return True
    except Exception as e:
        logger.error(f"关闭所有数据库连接时出错: {str(e)}")
        return False

def get_connection_stats():
    """获取数据库连接统计信息"""
    try:
        pool = get_connection_pool()
        return pool.get_stats()
    except Exception as e:
        logger.error(f"获取连接统计信息失败: {str(e)}")
        return {}

def check_connection_leaks(timeout_seconds=300):
    """检查连接泄漏"""
    try:
        pool = get_connection_pool()
        return pool.check_for_leaks(timeout_seconds)
    except Exception as e:
        logger.error(f"检查连接泄漏失败: {str(e)}")
        return []