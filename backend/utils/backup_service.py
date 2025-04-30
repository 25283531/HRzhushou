import os
import shutil
import sqlite3
import json
from datetime import datetime
import time
import threading
from database.db import DATABASE_PATH, get_db_connection, execute_query, get_current_time

class BackupService:
    """数据备份服务，提供数据自动备份功能"""
    
    def __init__(self):
        # 备份目录
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 自动备份间隔（小时）
        self.auto_backup_interval = 12
        
        # 自动备份线程
        self.auto_backup_thread = None
        self.stop_auto_backup = False
    
    def create_backup(self, description=None):
        """创建数据库备份
        
        Args:
            description: 备份描述
            
        Returns:
            备份文件名
        """
        # 检查数据库文件是否存在
        if not os.path.exists(DATABASE_PATH):
            raise FileNotFoundError(f"数据库文件不存在: {DATABASE_PATH}")
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # 复制数据库文件
        shutil.copy2(DATABASE_PATH, backup_path)
        
        # 记录备份信息到数据库
        if description is None:
            description = f"自动备份 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        query = '''
        INSERT INTO backups (filename, description, created_at)
        VALUES (?, ?, ?)
        '''
        
        current_time = get_current_time()
        execute_query(query, (backup_filename, description, current_time))
        
        return backup_filename
    
    def restore_backup(self, backup_filename):
        """从备份恢复数据库
        
        Args:
            backup_filename: 备份文件名
            
        Returns:
            是否成功恢复
        """
        # 检查备份文件是否存在
        backup_path = os.path.join(self.backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        
        # 关闭所有数据库连接
        # 这里需要确保没有活动的数据库连接
        # 在实际应用中，可能需要更复杂的机制来确保这一点
        
        # 备份当前数据库（以防恢复失败）
        current_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        current_backup_path = os.path.join(self.backup_dir, current_backup)
        shutil.copy2(DATABASE_PATH, current_backup_path)
        
        try:
            # 复制备份文件到数据库文件
            shutil.copy2(backup_path, DATABASE_PATH)
            return True
        except Exception as e:
            # 恢复失败，还原之前的数据库
            shutil.copy2(current_backup_path, DATABASE_PATH)
            raise e
    
    def get_all_backups(self):
        """获取所有备份记录
        
        Returns:
            备份记录列表
        """
        query = 'SELECT * FROM backups ORDER BY created_at DESC'
        return execute_query(query)
    
    def delete_backup(self, backup_id):
        """删除备份
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否成功删除
        """
        # 获取备份记录
        query = 'SELECT * FROM backups WHERE id = ?'
        backup = execute_query(query, (backup_id,), one=True)
        
        if not backup:
            raise ValueError(f"找不到ID为{backup_id}的备份记录")
        
        # 删除备份文件
        backup_path = os.path.join(self.backup_dir, backup['filename'])
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        # 删除备份记录
        query = 'DELETE FROM backups WHERE id = ?'
        execute_query(query, (backup_id,))
        
        return True
    
    def start_auto_backup(self):
        """启动自动备份线程"""
        if self.auto_backup_thread is not None and self.auto_backup_thread.is_alive():
            return
        
        self.stop_auto_backup = False
        self.auto_backup_thread = threading.Thread(target=self._auto_backup_task)
        self.auto_backup_thread.daemon = True
        self.auto_backup_thread.start()
    
    def stop_auto_backup_task(self):
        """停止自动备份线程"""
        self.stop_auto_backup = True
        if self.auto_backup_thread is not None:
            self.auto_backup_thread.join(timeout=1)
    
    def _auto_backup_task(self):
        """自动备份任务"""
        while not self.stop_auto_backup:
            try:
                # 创建自动备份
                self.create_backup("自动备份")
                
                # 清理过期备份（保留最近10个自动备份）
                self._cleanup_old_backups()
                
                # 等待下一次备份
                for _ in range(int(self.auto_backup_interval * 3600)):
                    if self.stop_auto_backup:
                        break
                    time.sleep(1)
            except Exception as e:
                # 记录错误但不中断线程
                from .error_handler import ErrorHandler
                ErrorHandler.log_error(e, "自动备份任务")
                
                # 等待一段时间后重试
                time.sleep(300)  # 5分钟后重试
    
    def _cleanup_old_backups(self, keep_count=10):
        """清理过期的自动备份
        
        Args:
            keep_count: 保留的自动备份数量
        """
        # 获取所有自动备份
        query = "SELECT * FROM backups WHERE description LIKE '自动备份%' ORDER BY created_at DESC"
        backups = execute_query(query)
        
        # 如果自动备份数量超过保留数量，删除最旧的备份
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                try:
                    self.delete_backup(backup['id'])
                except Exception as e:
                    # 记录错误但继续处理
                    from .error_handler import ErrorHandler
                    ErrorHandler.log_error(e, f"清理过期备份: {backup['id']}")

# 创建全局备份服务实例
backup_service = BackupService()

# 应用启动时启动自动备份
def start_auto_backup():
    backup_service.start_auto_backup()

# 应用关闭时停止自动备份
def stop_auto_backup():
    backup_service.stop_auto_backup_task()