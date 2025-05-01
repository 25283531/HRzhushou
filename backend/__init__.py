# HR助手后端包初始化文件
# 确保Python将此目录视为包

from flask import Flask
from flask_cors import CORS
from .utils.backup_service import start_auto_backup
from .utils.error_handler import register_error_handlers

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 启用CORS
    CORS(app)
    
    # 启动自动备份服务
    start_auto_backup()
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    return app

def register_blueprints(app):
    """注册所有蓝图"""
    from .routes.attendance import attendance_bp
    from .routes.employee import employee_bp
    from .routes.salary import salary_bp
    from .routes.social_security import social_security_bp
    
    # 注册蓝图
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(employee_bp, url_prefix='/api/employee')
    app.register_blueprint(salary_bp, url_prefix='/api/salary')
    app.register_blueprint(social_security_bp, url_prefix='/api/social-security')