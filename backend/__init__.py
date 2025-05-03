# HR助手后端包初始化文件
# 确保Python将此目录视为包

import sys
import traceback
from flask import Flask # type: ignore
from flask_cors import CORS

# 致命错误处理函数
def handle_fatal_error(error_message, exception=None):
    """处理致命错误，打印错误信息并退出程序"""
    print(f"\n致命错误: {error_message}")
    if exception:
        print(f"异常详情: {str(exception)}")
        traceback.print_exc()
    print("应用程序将退出...\n")
    sys.exit(1)

# 导入必要的模块，出错时立即退出
try:
    from .utils.backup_service import start_auto_backup
    from .utils.error_handler import register_error_handlers
except ImportError as e:
    handle_fatal_error("无法导入关键模块", e)

def create_app():
    """创建并配置Flask应用"""
    try:
        app = Flask(__name__)
        
        # 启用CORS
        try:
            CORS(app)
        except Exception as e:
            print(f"警告：启用CORS失败，跨域请求可能会被阻止。错误信息: {e}")
        
        # 启动自动备份服务
        try:
            start_auto_backup()
        except Exception as e:
            print(f"警告：启动自动备份服务失败。错误信息: {e}")
        
        # 注册错误处理器
        try:
            register_error_handlers(app)
        except Exception as e:
            handle_fatal_error("注册错误处理器失败", e)
        
        # 注册蓝图
        try:
            register_blueprints(app)
        except Exception as e:
            handle_fatal_error("注册蓝图失败", e)
        
        return app
    except Exception as e:
        handle_fatal_error("创建Flask应用失败", e)
        return None

def register_blueprints(app):
    """注册所有蓝图"""
    try:
        # 尝试导入所有路由模块
        from .routes.attendance import attendance_bp
        from .routes.employee import employee_bp
        from .routes.salary import salary_bp
        from .routes.social_security import social_security_bp
        
        # 注册蓝图
        app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
        app.register_blueprint(employee_bp, url_prefix='/api/employee')
        app.register_blueprint(salary_bp, url_prefix='/api/salary')
        app.register_blueprint(social_security_bp, url_prefix='/api/social-security')
    except ImportError as e:
        handle_fatal_error("无法导入路由模块，API无法正常工作", e)
    except Exception as e:
        handle_fatal_error("注册蓝图时发生未知错误", e)