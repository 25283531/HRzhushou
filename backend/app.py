import os
import sys
import traceback
import atexit
import signal
import threading
from flask import Flask
from flask_cors import CORS

# 全局错误标志，用于标记是否发生了致命错误
fatal_error_occurred = False

# 致命错误处理函数
def handle_fatal_error(error_message, exception=None):
    """处理致命错误，打印错误信息并退出程序"""
    global fatal_error_occurred
    fatal_error_occurred = True
    print(f"\n致命错误: {error_message}")
    if exception:
        print(f"异常详情: {str(exception)}")
        traceback.print_exc()
    print("应用程序将退出...\n")
    sys.exit(1)

# 创建Flask应用
try:
    app = Flask(__name__)
    CORS(app)
except Exception as e:
    handle_fatal_error("无法创建Flask应用", e)

# 导入数据库模块
try:
    # 确保项目根目录在Python路径中
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 尝试绝对导入
    from backend.database.db import init_db
    from backend.models.salary_items import create_tables
except ImportError as e:
    handle_fatal_error("无法导入数据库模块", e)

# 初始化数据库
@app.before_first_request
def setup():
    try:
        init_db()
        create_tables()
    except Exception as e:
        handle_fatal_error("数据库初始化失败", e)

# 注册路由
try:
    from backend.routes.attendance import attendance_bp
    from backend.routes.employee import employee_bp
    from backend.routes.salary import salary_bp
    from backend.routes.social_security import social_security_bp
    from backend.routes.salary_items import bp as salary_items_bp
    from backend.routes.position_levels import bp as position_levels_bp
    
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(employee_bp, url_prefix='/api/employee')
    app.register_blueprint(salary_bp, url_prefix='/api/salary')
    app.register_blueprint(social_security_bp, url_prefix='/api/social-security')
    app.register_blueprint(salary_items_bp, url_prefix='/api/salary-items')
    app.register_blueprint(position_levels_bp, url_prefix='/api/position-levels')
except ImportError as e:
    handle_fatal_error("无法导入路由模块", e)

# 添加全局异常处理
@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理器，捕获未处理的异常"""
    print(f"\n未处理的异常: {str(e)}")
    traceback.print_exc()
    return {"error": "服务器内部错误", "message": str(e)}, 500

# 导入应用生命周期管理器
try:
    from backend.utils.app_lifecycle import start_app_services, stop_app_services, cleanup
    
    # 注册应用退出时的清理函数
    @atexit.register
    def cleanup_on_exit():
        print("\n正在关闭应用程序，清理资源...")
        try:
            # 停止所有应用服务
            stop_app_services()
            print("所有应用服务已停止")
            
            # 清理所有资源
            cleanup()
            print("所有资源已清理完毕")
        except Exception as e:
            print(f"应用程序清理过程中出错: {str(e)}")
            traceback.print_exc()
        
        # 关闭所有数据库连接
        try:
            # 尝试获取一个新连接并立即关闭，确保SQLite释放所有资源
            from backend.database.db import get_db_connection
            conn = get_db_connection()
            conn.close()
            print("数据库连接已关闭")
        except Exception as e:
            print(f"关闭数据库连接时出错: {str(e)}")
            
        print("应用程序已安全退出")
except ImportError as e:
    print(f"警告：无法导入备份服务函数: {str(e)}")

# 启动所有应用服务
try:
    # 应用启动时启动所有服务
    start_app_services()
    print("所有应用服务已启动")
except Exception as e:
    print(f"启动应用服务失败: {str(e)}")
    traceback.print_exc()
    # 不抛出异常，让应用程序继续运行

# 添加信号处理函数
def signal_handler(sig, frame):
    """处理终止信号，确保应用程序能够正常退出"""
    print(f"\n接收到信号 {signal.Signals(sig).name}，正在关闭应用程序...")
    # 停止所有应用服务
    try:
        from backend.utils.app_lifecycle import stop_app_services, cleanup
        stop_app_services()
        cleanup()
    except Exception as e:
        print(f"停止应用服务时出错: {str(e)}")
    sys.exit(0)

# 注册信号处理函数
if os.name == 'nt':  # Windows系统
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError) as e:
        print(f"注册信号处理函数时出错: {str(e)}")
else:  # 类Unix系统
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)
    except (AttributeError, ValueError) as e:
        print(f"注册信号处理函数时出错: {str(e)}")

# 创建一个事件用于控制主线程退出
exit_event = threading.Event()

# 应用入口点
if __name__ == '__main__':
    # 检查是否发生了致命错误
    if fatal_error_occurred:
        sys.exit(1)
    
    try:
        print("正在启动HR助手后端服务...")
        # 使用线程运行Flask应用
        server_thread = threading.Thread(target=lambda: app.run(debug=True, port=5566, use_reloader=False))
        server_thread.daemon = True
        server_thread.start()
        
        # 主线程等待退出信号
        try:
            while server_thread.is_alive():
                if exit_event.wait(1):
                    break
        except KeyboardInterrupt:
            print("\n接收到键盘中断，正在关闭应用程序...")
        finally:
            # 确保在主线程退出前清理资源
            try:
                from backend.utils.app_lifecycle import stop_app_services, cleanup
                stop_app_services()
                cleanup()
                print("应用程序已安全退出")
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
    except Exception as e:
        handle_fatal_error("启动服务器时发生错误", e)