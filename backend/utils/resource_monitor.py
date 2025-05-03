import os
import psutil
import threading
import time
import logging
from datetime import datetime

# 尝试多种导入方式
try:
    # 尝试相对导入
    from .error_handler import ErrorHandler
    from .thread_manager import get_thread_manager
except ImportError:
    try:
        # 尝试从项目根目录导入
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from backend.utils.error_handler import ErrorHandler
        from backend.utils.thread_manager import get_thread_manager
    except ImportError:
        # 最后尝试直接导入
        from utils.error_handler import ErrorHandler
        from utils.thread_manager import get_thread_manager

class ResourceMonitor:
    """资源监控器，用于监控应用程序的资源使用情况
    
    该类提供对CPU、内存、磁盘和数据库连接等资源的监控功能，
    并在资源使用超过阈值时发出警告，帮助及时发现资源泄漏问题。
    """
    
    def __init__(self, interval=60, log_dir=None):
        """初始化资源监控器
        
        Args:
            interval: 监控间隔（秒），默认为60秒
            log_dir: 日志目录，默认为None（使用应用程序默认日志目录）
        """
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        
        # 设置日志目录
        if log_dir is None:
            self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        else:
            self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 配置资源监控日志
        self.logger = logging.getLogger('hrzhushou.resource_monitor')
        
        # 设置资源使用阈值
        self.cpu_threshold = 80  # CPU使用率阈值（百分比）
        self.memory_threshold = 80  # 内存使用率阈值（百分比）
        self.disk_threshold = 90  # 磁盘使用率阈值（百分比）
        
        # 获取线程管理器
        self.thread_manager = get_thread_manager('resource_monitor')
    
    def start_monitoring(self):
        """启动资源监控"""
        if self.thread_manager.is_running():
            self.logger.info("资源监控已经在运行中")
            return
        
        self.logger.info("启动资源监控服务")
        self.thread_manager.start(target=self._monitoring_task)
    
    def stop_monitoring(self):
        """停止资源监控"""
        self.logger.info("停止资源监控服务")
        return self.thread_manager.stop()
    
    def _monitoring_task(self):
        """资源监控任务"""
        self.logger.info("资源监控任务已启动")
        
        while not self.thread_manager.should_stop():
            try:
                # 收集资源使用情况
                cpu_percent = self.process.cpu_percent(interval=1)
                memory_info = self.process.memory_info()
                memory_percent = self.process.memory_percent()
                
                # 获取磁盘使用情况
                disk_usage = psutil.disk_usage(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                disk_percent = disk_usage.percent
                
                # 记录资源使用情况
                self._log_resource_usage(cpu_percent, memory_info, memory_percent, disk_percent)
                
                # 检查资源使用是否超过阈值
                self._check_resource_thresholds(cpu_percent, memory_percent, disk_percent)
                
                # 等待下一次监控，同时检查停止信号
                check_interval = 1  # 每秒检查一次停止信号
                for _ in range(int(self.interval / check_interval)):
                    if self.thread_manager.should_stop():
                        break
                    time.sleep(check_interval)
            except Exception as e:
                # 记录错误但不中断监控
                ErrorHandler.log_error(e, "资源监控任务")
                self.logger.error(f"资源监控任务出错: {str(e)}")
                
                # 等待一段时间后重试
                retry_wait = 30  # 30秒后重试
                for _ in range(retry_wait):
                    if self.thread_manager.should_stop():
                        break
                    time.sleep(1)
        
        self.logger.info("资源监控任务已退出")
    
    def _log_resource_usage(self, cpu_percent, memory_info, memory_percent, disk_percent):
        """记录资源使用情况
        
        Args:
            cpu_percent: CPU使用率（百分比）
            memory_info: 内存使用信息
            memory_percent: 内存使用率（百分比）
            disk_percent: 磁盘使用率（百分比）
        """
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 转换内存使用量为MB
        memory_mb = memory_info.rss / 1024 / 1024
        
        # 记录资源使用情况
        self.logger.info(f"[{current_time}] 资源使用情况 - CPU: {cpu_percent:.1f}%, 内存: {memory_mb:.1f}MB ({memory_percent:.1f}%), 磁盘: {disk_percent:.1f}%")
        
        # 每天创建一个新的资源使用日志文件
        log_date = datetime.now().strftime('%Y%m%d')
        resource_log_file = os.path.join(self.log_dir, f'resource_{log_date}.log')
        
        # 将资源使用情况写入日志文件
        with open(resource_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{current_time},CPU,{cpu_percent:.1f}%\n")
            f.write(f"{current_time},内存,{memory_mb:.1f}MB,{memory_percent:.1f}%\n")
            f.write(f"{current_time},磁盘,{disk_percent:.1f}%\n")
    
    def _check_resource_thresholds(self, cpu_percent, memory_percent, disk_percent):
        """检查资源使用是否超过阈值
        
        Args:
            cpu_percent: CPU使用率（百分比）
            memory_percent: 内存使用率（百分比）
            disk_percent: 磁盘使用率（百分比）
        """
        # 检查CPU使用率
        if cpu_percent > self.cpu_threshold:
            self.logger.warning(f"警告：CPU使用率过高 ({cpu_percent:.1f}% > {self.cpu_threshold}%)")
        
        # 检查内存使用率
        if memory_percent > self.memory_threshold:
            self.logger.warning(f"警告：内存使用率过高 ({memory_percent:.1f}% > {self.memory_threshold}%)")
        
        # 检查磁盘使用率
        if disk_percent > self.disk_threshold:
            self.logger.warning(f"警告：磁盘使用率过高 ({disk_percent:.1f}% > {self.disk_threshold}%)")

# 全局资源监控器实例
resource_monitor = None

def start_resource_monitoring(interval=60):
    """启动资源监控
    
    Args:
        interval: 监控间隔（秒），默认为60秒
    """
    global resource_monitor
    if resource_monitor is None:
        resource_monitor = ResourceMonitor(interval)
    resource_monitor.start_monitoring()

def stop_resource_monitoring():
    """停止资源监控"""
    global resource_monitor
    if resource_monitor is not None:
        return resource_monitor.stop_monitoring()
    return True