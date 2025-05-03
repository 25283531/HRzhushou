import os
import shutil
import sqlite3
import json
from datetime import datetime
import time
import threading
import sys
import logging

# 尝试多种导入方式
try:
    # 尝试相对导入
    from ..database.db import DATABASE_PATH, get_db_connection, execute_query, get_current_time
    from .error_handler import ErrorHandler
    from .thread_manager import get_thread_manager
except ImportError:
    try:
        # 尝试从项目根目录导入
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from backend.database.db import DATABASE_PATH, get_db_connection, execute_query, get_current_time
        from backend.utils.error_handler import ErrorHandler
        from backend.utils.thread_manager import get_thread_manager
    except ImportError:
        # 最后尝试直接导入
        from database.db import DATABASE_PATH, get_db_connection, execute_query, get_current_time
        from utils.error_handler import ErrorHandler
        from utils.thread_manager import get_thread_manager

class BackupService:
    """数据备份服务，提供数据自动备份功能"""
    
    def __init__(self):
        # 备份目录
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 自动备份间隔（小时）
        self.auto_backup_interval = 12
        
        # 获取线程管理器
        self.thread_manager = get_thread_manager('backup_service')
        
        # 配置日志
        self.logger = logging.getLogger('hrzhushou.backup_service')
    
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
        try:
            # 使用连接池的close_all方法关闭所有连接
            from ..database.db import close_all_connections
            close_all_connections()
            self.logger.info("已关闭所有数据库连接")
        except Exception as e:
            self.logger.error(f"关闭数据库连接时出错: {str(e)}")
            # 即使出错也继续执行，尝试恢复操作
        
        # 备份当前数据库（以防恢复失败）
        current_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        current_backup_path = os.path.join(self.backup_dir, current_backup)
        shutil.copy2(DATABASE_PATH, current_backup_path)
        print(f"已创建恢复前备份: {current_backup}")
        
        try:
            # 复制备份文件到数据库文件
            shutil.copy2(backup_path, DATABASE_PATH)
            print(f"已成功从备份 {backup_filename} 恢复数据库")
            return True
        except Exception as e:
            # 恢复失败，还原之前的数据库
            print(f"恢复失败，正在还原到之前的数据库状态: {str(e)}")
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
        if self.thread_manager.is_running():
            self.logger.info("备份线程已经在运行中，无需重新启动")
            return
        
        self.logger.info("启动自动备份服务")
        self.thread_manager.start(target=self._auto_backup_task)
    
    def stop_auto_backup_task(self):
        """停止自动备份线程"""
        self.logger.info("停止自动备份服务")
        return self.thread_manager.stop()
    
    def _auto_backup_task(self):
        """自动备份任务"""
        self.logger.info("自动备份任务已启动")
        while not self.thread_manager.should_stop():
            try:
                # 创建自动备份
                self.create_backup("自动备份")
                self.logger.info(f"自动备份已完成，下次备份将在{self.auto_backup_interval}小时后进行")
                
                # 清理过期备份（保留最近10个自动备份）
                self._cleanup_old_backups()
                
                # 等待下一次备份，使用更小的时间间隔检查停止标志，确保能够及时响应停止请求
                check_interval = 5  # 秒
                checks_needed = int(self.auto_backup_interval * 3600 / check_interval)
                
                for i in range(checks_needed):
                    if self.thread_manager.should_stop():
                        self.logger.info("检测到停止信号，自动备份任务正在退出...")
                        break
                    # 每10分钟输出一次等待信息，便于调试
                    if i % (600 // check_interval) == 0 and i > 0:
                        self.logger.info(f"自动备份等待中...下次备份将在{self.auto_backup_interval - (i * check_interval / 3600):.1f}小时后进行")
                    time.sleep(check_interval)
            except Exception as e:
                # 记录错误但不中断线程
                ErrorHandler.log_error(e, "自动备份任务")
                self.logger.error(f"自动备份任务出错: {str(e)}")
                
                # 等待一段时间后重试，同时检查停止信号
                retry_wait = 120  # 2分钟后重试
                retry_check_interval = 2  # 每2秒检查一次停止信号
                self.logger.info(f"将在{retry_wait}秒后重试备份任务...")
                
                for i in range(int(retry_wait / retry_check_interval)):
                    if self.thread_manager.should_stop():
                        self.logger.info("检测到停止信号，自动备份任务正在退出...")
                        break
                    # 每30秒输出一次等待信息
                    if i % (30 // retry_check_interval) == 0 and i > 0:
                        self.logger.info(f"备份任务重试等待中...将在{retry_wait - (i * retry_check_interval)}秒后重试")
                    time.sleep(retry_check_interval)
        
        self.logger.info("自动备份任务已退出")

    
    def _cleanup_old_backups(self, keep_count=10):
        """清理过期的自动备份
        
        Args:
            keep_count: 保留的自动备份数量
        """
        # 如果正在停止，直接返回，避免不必要的操作
        if self.thread_manager.should_stop():
            self.logger.info("检测到停止信号，跳过清理过期备份")
            return
            
        try:
            # 获取所有自动备份
            query = "SELECT * FROM backups WHERE description LIKE '自动备份%' ORDER BY created_at DESC"
            backups = execute_query(query)
            
            # 如果自动备份数量超过保留数量，删除最旧的备份
            if len(backups) > keep_count:
                self.logger.info(f"清理过期备份，当前有{len(backups)}个自动备份，将保留最新的{keep_count}个")
                # 限制每次清理的数量，避免长时间阻塞
                to_delete = backups[keep_count:keep_count+5]  # 每次最多删除5个
                
                for backup in to_delete:
                    # 再次检查停止信号，确保能够及时响应
                    if self.thread_manager.should_stop():
                        self.logger.info("检测到停止信号，中断清理过期备份")
                        return
                        
                    try:
                        self.delete_backup(backup['id'])
                        self.logger.info(f"已删除过期备份: {backup['filename']}")
                    except Exception as e:
                        # 记录错误但继续处理
                        ErrorHandler.log_error(e, f"清理过期备份: {backup['id']}")
                        self.logger.error(f"清理过期备份出错: {str(e)}")
        except Exception as e:
            # 捕获所有异常，确保不会因为清理备份失败而中断备份线程
            ErrorHandler.log_error(e, "清理过期备份过程")
            self.logger.error(f"清理过期备份过程出错: {str(e)}")
            # 即使出错也不影响主线程继续运行

# 创建全局备份服务实例
backup_service = BackupService()

# 提供给应用程序调用的函数
def start_auto_backup():
    """启动自动备份服务"""
    backup_service.start_auto_backup()

# 应用关闭时停止自动备份
def stop_auto_backup():
    """停止自动备份服务"""
    return backup_service.stop_auto_backup_task()

# 获取备份服务实例
def get_backup_service():
    """获取备份服务实例"""
    return backup_service