import logging
import os
import traceback
from datetime import datetime

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'error.log')
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('hrzhushou')

class ErrorHandler:
    """错误处理服务，提供统一的错误处理机制"""
    
    @staticmethod
    def log_error(error, context=None):
        """记录错误日志
        
        Args:
            error: 错误对象或错误消息
            context: 错误上下文信息
        """
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # 记录到日志文件
        if context:
            logger.error(f"Error: {error_message}\nContext: {context}\nTraceback: {error_traceback}")
        else:
            logger.error(f"Error: {error_message}\nTraceback: {error_traceback}")
    
    @staticmethod
    def format_user_error(error):
        """格式化用户友好的错误消息
        
        Args:
            error: 错误对象或错误消息
            
        Returns:
            用户友好的错误消息
        """
        error_message = str(error)
        
        # 常见错误类型的友好提示
        if 'no such table' in error_message.lower():
            return "数据库表不存在，请确保已正确初始化数据库"
        
        if 'unique constraint' in error_message.lower():
            return "数据已存在，请勿重复添加"
        
        if 'foreign key constraint' in error_message.lower():
            return "操作失败，该记录被其他数据引用"
        
        if 'permission denied' in error_message.lower():
            return "权限不足，无法执行该操作"
        
        if 'disk full' in error_message.lower():
            return "磁盘空间不足，请清理空间后重试"
        
        # 特定业务错误的友好提示
        if '找不到员工' in error_message:
            return "找不到指定的员工，请检查员工信息"
        
        if '日期格式不正确' in error_message:
            return "日期格式不正确，请使用YYYY-MM-DD格式"
        
        if '缺少必要的字段' in error_message:
            return "数据不完整，请填写所有必要信息"
        
        # 默认错误提示
        return f"操作失败: {error_message}"
    
    @staticmethod
    def handle_exception(func):
        """异常处理装饰器
        
        用于包装API函数，统一处理异常
        
        Args:
            func: 被装饰的函数
            
        Returns:
            包装后的函数
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录错误
                ErrorHandler.log_error(e, {
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                })
                
                # 返回友好的错误消息
                error_message = ErrorHandler.format_user_error(e)
                from flask import jsonify
                return jsonify({
                    'success': False,
                    'error': error_message
                }), 400
        
        return wrapper