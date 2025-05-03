import threading
import time
import logging
import traceback
import os
from datetime import datetime

# 尝试多种导入方式
try:
    # 尝试相对导入
    from .error_handler import ErrorHandler
except ImportError:
    try:
        # 尝试从项目根目录导入
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from backend.utils.error_handler import ErrorHandler
    except ImportError:
        # 最后尝试直接导入
        from utils.error_handler import ErrorHandler

class ThreadManager:
    """线程管理器，提供统一的线程管理和资源处理机制
    
    该类用于管理后台线程，确保它们能够正确响应停止信号，并在发生异常时进行适当的错误处理。
    同时提供资源管理功能，确保所有资源（如数据库连接、文件句柄等）在使用后都被正确关闭。
    """
    
    def __init__(self, name="未命名线程", daemon=True):
        """初始化线程管理器
        
        Args:
            name: 线程名称，用于日志记录和调试
            daemon: 是否为守护线程，默认为True
        """
        self.name = name
        self.daemon = daemon
        self.thread = None
        self.stop_flag = False
        self.resources = []
        self.logger = logging.getLogger('hrzhushou.thread_manager')
    
    def start(self, target, args=(), kwargs={}):
        """启动线程
        
        Args:
            target: 线程目标函数
            args: 传递给目标函数的位置参数
            kwargs: 传递给目标函数的关键字参数
            
        Returns:
            线程对象
        """
        if self.thread is not None and self.thread.is_alive():
            self.logger.warning(f"线程 '{self.name}' 已经在运行中，无需重新启动")
            return self.thread
        
        # 重置停止标志
        self.stop_flag = False
        
        # 创建包装函数，添加错误处理和资源管理
        def wrapped_target(*args, **kwargs):
            try:
                self.logger.info(f"线程 '{self.name}' 已启动")
                target(*args, **kwargs)
            except Exception as e:
                # 记录错误但不中断线程
                ErrorHandler.log_error(e, f"线程 '{self.name}' 执行过程中出错")
                self.logger.error(f"线程 '{self.name}' 执行出错: {str(e)}")
                self.logger.error(traceback.format_exc())
            finally:
                # 确保所有资源都被释放
                self.close_all_resources()
                self.logger.info(f"线程 '{self.name}' 已退出")
        
        # 创建并启动线程
        self.thread = threading.Thread(target=wrapped_target, args=args, kwargs=kwargs)
        self.thread.daemon = self.daemon
        self.thread.name = self.name
        self.thread.start()
        
        return self.thread
    
    def stop(self, timeout=15, check_interval=3):
        """停止线程
        
        Args:
            timeout: 等待线程停止的最大时间（秒）
            check_interval: 检查线程状态的时间间隔（秒）
            
        Returns:
            是否成功停止线程
        """
        # 先检查线程状态
        if self.thread is None:
            self.logger.info(f"线程 '{self.name}' 未启动，无需停止")
            return True
            
        if not self.thread.is_alive():
            self.logger.info(f"线程 '{self.name}' 已经停止运行")
            self.thread = None
            return True
            
        # 设置停止标志
        self.stop_flag = True
        self.logger.info(f"正在等待线程 '{self.name}' 安全退出...")
        
        try:
            # 分段等待，每次等待check_interval秒检查一次状态
            for i in range(int(timeout / check_interval)):
                self.thread.join(timeout=check_interval)
                if not self.thread.is_alive():
                    self.logger.info(f"线程 '{self.name}' 已成功停止")
                    self.thread = None
                    return True
                self.logger.info(f"线程 '{self.name}' 仍在运行，继续等待...({(i+1)*check_interval}/{timeout}秒)")
            
            # 如果超时后线程仍在运行
            if self.thread.is_alive():
                self.logger.warning(f"警告：线程 '{self.name}' 未能在指定时间内停止，正在强制终止")
                # 由于线程被设置为daemon=True，应用程序退出时线程会自动终止
                # 清除线程引用，避免应用程序因等待线程而阻塞
                self.thread = None
                self.logger.info(f"已清除线程 '{self.name}' 引用，应用程序可以正常退出")
                return False
            else:
                self.logger.info(f"线程 '{self.name}' 已成功停止")
                self.thread = None
                return True
        except Exception as e:
            self.logger.error(f"停止线程 '{self.name}' 时出错: {str(e)}")
            # 确保线程引用被清除，避免后续操作时出错
            self.thread = None
            self.logger.info(f"已清除线程 '{self.name}' 引用，应用程序可以正常退出")
            return False
    
    def is_running(self):
        """检查线程是否正在运行
        
        Returns:
            线程是否正在运行
        """
        return self.thread is not None and self.thread.is_alive()
    
    def should_stop(self):
        """检查是否应该停止线程
        
        Returns:
            是否应该停止线程
        """
        return self.stop_flag
    
    def register_resource(self, resource, close_method='close'):
        """注册需要管理的资源
        
        Args:
            resource: 需要管理的资源对象
            close_method: 关闭资源的方法名，默认为'close'
            
        Returns:
            资源对象
        """
        self.resources.append((resource, close_method))
        return resource
    
    def close_resource(self, resource):
        """关闭指定资源
        
        Args:
            resource: 需要关闭的资源对象
            
        Returns:
            是否成功关闭资源
        """
        for r, close_method in self.resources:
            if r == resource:
                try:
                    # 调用资源的关闭方法
                    getattr(r, close_method)()
                    self.resources.remove((r, close_method))
                    return True
                except Exception as e:
                    self.logger.error(f"关闭资源时出错: {str(e)}")
                    return False
        return False
    
    def close_all_resources(self):
        """关闭所有资源
        
        Returns:
            是否成功关闭所有资源
        """
        success = True
        resources_to_remove = []
        
        for resource, close_method in self.resources:
            try:
                # 调用资源的关闭方法
                getattr(resource, close_method)()
                resources_to_remove.append((resource, close_method))
            except Exception as e:
                self.logger.error(f"关闭资源时出错: {str(e)}")
                success = False
        
        # 从资源列表中移除已关闭的资源
        for r in resources_to_remove:
            self.resources.remove(r)
        
        return success

# 全局线程管理器字典，用于跟踪所有线程
thread_managers = {}

def get_thread_manager(name, daemon=True):
    """获取指定名称的线程管理器
    
    Args:
        name: 线程名称
        daemon: 是否为守护线程，默认为True
        
    Returns:
        线程管理器对象
    """
    if name not in thread_managers:
        thread_managers[name] = ThreadManager(name, daemon)
    return thread_managers[name]

def stop_all_threads(timeout=30):
    """停止所有线程
    
    Args:
        timeout: 等待每个线程停止的最大时间（秒）
        
    Returns:
        是否成功停止所有线程
    """
    logger = logging.getLogger('hrzhushou.thread_manager')
    logger.info("正在停止所有后台线程...")
    
    success = True
    for name, manager in thread_managers.items():
        if manager.is_running():
            logger.info(f"正在停止线程 '{name}'...")
            if not manager.stop(timeout):
                logger.warning(f"无法正常停止线程 '{name}'")
                success = False
    
    return success

# 应用程序退出时调用此函数
def cleanup():
    """清理所有资源并停止所有线程"""
    stop_all_threads()