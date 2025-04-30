# HR助手后端包初始化文件
# 确保Python将此目录视为包

from flask import Flask
from flask_cors import CORS
from .utils.backup_service import start_auto_backup

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 启用CORS
    CORS(app)
    
    # 启动自动备份服务
    start_auto_backup()
    
    return app