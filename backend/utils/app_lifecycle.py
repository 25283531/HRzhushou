import os
import sys
import logging
import atexit
import signal
import time
from datetime import datetime

# 尝试多种导入方式
try:
    # 尝试相对导入
    from .thread_manager import stop_all_threads, cleanup
    from .resource_monitor import start_resource_monitoring, stop_resource_monitoring
    from .backup_service import start_auto_backup, stop_auto_backup
    from .error_handler import ErrorHandler
    from ..database.db import close_all_connections, get_connection_stats, check_connection_leaks
except ImportError:
    try:
        # 尝试从项目根目录导入
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from backend.utils.thread_manager import stop_all_threads, cleanup
        from backend.utils.resource_monitor import start_resource_monitoring, stop_resource_monitoring
        from backend.utils.backup_service import start_auto_backup, stop_auto_backup
        from backend.utils.error_handler import ErrorHandler
        from backend.database.db import close_all_connections, get_connection_stats, check_connection_leaks
    except ImportError:
        # 最后尝试直接导入
        from utils.thread_manager import stop_all_threads, cleanup
        from utils.resource_monitor import start_resource_monitoring, stop_resource_monitoring
        from utils.backup_service import start_auto_backup, stop_auto_backup
        from utils.error_handler import ErrorHandler
        from database.db import close_all_connections, get_connection_stats, check_connection_leaks

class AppLifecycleManager:
    """应用程序生命周期管理器
    
    负责管理应用程序的启动和关闭过程，确保所有资源都能够正确初始化和释放。
    提供统一的接口来启动和停止所有后台服务，并在应用程序退出时进行清理。
    """
    
    def __init__(self):
        """初始化应用程序生命周期管理器"""
        self.logger = logging.getLogger('hrzhushou.app_lifecycle')
        self.services_started = False
        self.exit_handlers_registered = False
        
        # 配置日志
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 应用启动时间
        self.start_time = datetime.now()
    
    def start_services(self):
        """启动所有后台服务"""
        if self.services_started:
            self.logger.info("后台服务已经启动，无需重复启动")
            return
        
        try:
            self.logger.info("正在启动所有后台服务...")
            
            # 启动资源监控
            start_resource_monitoring()
            self.logger.info("资源监控服务已启动")
            
            # 启动自动备份
            start_auto_backup()
            self.logger.info("自动备份服务已启动")
            
            # 启动数据库连接监控
            self._start_db_connection_monitoring()
            self.logger.info("数据库连接监控已启动")
            
            # 注册退出处理函数
            if not self.exit_handlers_registered:
                self._register_exit_handlers()
                self.exit_handlers_registered = True
            
            self.services_started = True
            self.logger.info("所有后台服务已成功启动")
            
            # 记录应用启动信息
            self._log_startup_info()
            
            return True
        except Exception as e:
            ErrorHandler.log_error(e, "启动后台服务")
            self.logger.error(f"启动后台服务时出错: {str(e)}")
            return False
    
    def stop_services(self):
        """停止所有后台服务"""
        if not self.services_started:
            self.logger.info("后台服务尚未启动，无需停止")
            return True
        
        try:
            self.logger.info("正在停止所有后台服务...")
            
            # 停止自动备份
            backup_result = stop_auto_backup()
            self.logger.info(f"自动备份服务停止{'成功' if backup_result else '失败'}")
            
            # 停止资源监控
            monitor_result = stop_resource_monitoring()
            self.logger.info(f"资源监控服务停止{'成功' if monitor_result else '失败'}")
            
            # 停止所有其他线程
            threads_result = stop_all_threads()
            self.logger.info(f"所有后台线程停止{'成功' if threads_result else '部分失败'}")
            
            self.services_started = False
            self.logger.info("所有后台服务已停止")
            
            # 记录应用关闭信息
            self._log_shutdown_info()
            
            return backup_result and monitor_result and threads_result
        except Exception as e:
            ErrorHandler.log_error(e, "停止后台服务")
            self.logger.error(f"停止后台服务时出错: {str(e)}")
            return False
    
    def _register_exit_handlers(self):
        """注册应用程序退出处理函数"""
        # 注册atexit处理函数
        atexit.register(self._exit_handler)
        
        # 注册信号处理函数（仅在非Windows系统上）
        if os.name != 'nt':
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        
        self.logger.info("已注册应用程序退出处理函数")
    
    def _exit_handler(self):
        """应用程序退出处理函数"""
        self.logger.info("应用程序正在退出，执行清理操作...")
        
        # 检查数据库连接泄漏
        leaks = check_connection_leaks(timeout_seconds=60)  # 使用较短的超时时间
        if leaks:
            self.logger.warning(f"检测到 {len(leaks)} 个数据库连接可能泄漏")
        
        # 获取连接池状态
        conn_stats = get_connection_stats()
        self.logger.info(f"数据库连接池状态: {conn_stats}")
        
        # 停止所有服务
        self.stop_services()
        
        # 关闭所有数据库连接
        db_close_result = close_all_connections()
        self.logger.info(f"数据库连接关闭{'成功' if db_close_result else '失败'}")
        
        # 执行其他清理
        cleanup()
        
        self.logger.info("应用程序清理完成，准备退出")
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        sig_name = signal.Signals(signum).name
        self.logger.info(f"接收到信号 {sig_name}，准备退出应用程序")
        # 执行退出处理
        self._exit_handler()
        # 正常退出程序
        sys.exit(0)
    
    def _log_startup_info(self):
        """记录应用启动信息"""
        self.logger.info(f"应用程序启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Python版本: {sys.version}")
        self.logger.info(f"运行平台: {sys.platform}")
        self.logger.info(f"工作目录: {os.getcwd()}")
    
    def _log_shutdown_info(self):
        """记录应用关闭信息"""
        end_time = datetime.now()
        run_time = end_time - self.start_time
        hours, remainder = divmod(run_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        self.logger.info(f"应用程序关闭时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"应用程序运行时长: {int(hours)}小时{int(minutes)}分钟{int(seconds)}秒")
    
    def _start_db_connection_monitoring(self):
        """启动数据库连接监控"""
        try:
            # 定期检查数据库连接泄漏
            def monitor_db_connections():
                from threading import Timer
                import time
                
                # 每10分钟检查一次连接泄漏
                while not stop_all_threads.is_stopping():
                    try:
                        # 检查连接泄漏
                        leaks = check_connection_leaks()
                        if leaks:
                            self.logger.warning(f"检测到 {len(leaks)} 个数据库连接可能泄漏")
                            
                        # 获取连接池状态
                        conn_stats = get_connection_stats()
                        self.logger.debug(f"数据库连接池状态: {conn_stats}")
                    except Exception as e:
                        self.logger.error(f"监控数据库连接时出错: {str(e)}")
                    
                    # 等待下一次检查
                    for _ in range(60):  # 每10分钟检查一次，但每10秒检查一次是否应该停止
                        if stop_all_threads.is_stopping():
                            break
                        time.sleep(10)
            
            # 启动监控线程
            from .thread_manager import get_thread_manager
            tm = get_thread_manager("db_connection_monitor")
            tm.start(target=monitor_db_connections)
        except Exception as e:
            self.logger.error(f"启动数据库连接监控失败: {str(e)}")

# 创建全局应用程序生命周期管理器实例
app_lifecycle_manager = AppLifecycleManager()

def start_app_services():
    """启动应用程序服务"""
    return app_lifecycle_manager.start_services()

def stop_app_services():
    """停止应用程序服务"""
    return app_lifecycle_manager.stop_services()

def get_app_lifecycle_manager():
    """获取应用程序生命周期管理器实例"""
    return app_lifecycle_manager