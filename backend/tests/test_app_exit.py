import os
import sys
import unittest
import threading
import time
import logging
import psutil
import sqlite3
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入需要测试的模块
from backend.utils.thread_manager import get_thread_manager, stop_all_threads, cleanup
from backend.utils.resource_monitor import start_resource_monitoring, stop_resource_monitoring
from backend.utils.backup_service import get_backup_service, start_auto_backup, stop_auto_backup
from backend.database.db import get_db_connection, execute_query, get_connection_pool, close_all_connections, get_connection_stats

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_app_exit')

class TestAppExit(unittest.TestCase):
    """测试应用程序退出行为
    
    这个测试类用于验证应用程序在各种情况下的退出行为，
    特别是检查资源是否正确释放，线程是否正确停止。
    """
    
    def setUp(self):
        """测试前准备"""
        # 确保所有线程都已停止
        stop_all_threads()
        # 等待一段时间，确保所有资源都已释放
        time.sleep(1)
    
    def tearDown(self):
        """测试后清理"""
        # 确保所有线程都已停止
        stop_all_threads()
        # 等待一段时间，确保所有资源都已释放
        time.sleep(1)
    
    def test_backup_service_stop(self):
        """测试备份服务能否正确停止"""
        # 启动备份服务
        start_auto_backup()
        # 等待一段时间，确保服务已启动
        time.sleep(2)
        
        # 获取备份服务实例
        backup_service = get_backup_service()
        # 验证服务是否正在运行
        self.assertTrue(backup_service.thread_manager.is_running(), "备份服务未正常启动")
        
        # 停止备份服务
        result = stop_auto_backup()
        # 验证服务是否已停止
        self.assertTrue(result, "备份服务未能正常停止")
        self.assertFalse(backup_service.thread_manager.is_running(), "备份服务线程仍在运行")
    
    def test_resource_monitor_stop(self):
        """测试资源监控服务能否正确停止"""
        # 启动资源监控
        start_resource_monitoring(interval=5)  # 设置较短的监控间隔，便于测试
        # 等待一段时间，确保服务已启动
        time.sleep(2)
        
        # 停止资源监控
        result = stop_resource_monitoring()
        # 验证服务是否已停止
        self.assertTrue(result, "资源监控服务未能正常停止")
    
    def test_database_connection_pool(self):
        """测试数据库连接池功能"""
        from backend.database.db import get_connection_pool, get_db_connection, close_all_connections, get_connection_stats
        
        # 获取连接池实例
        pool = get_connection_pool()
        self.assertIsNotNone(pool, "连接池实例不应为空")
        
        # 获取初始连接池状态
        initial_stats = get_connection_stats()
        self.assertIn('pool_size', initial_stats, "连接池统计信息应包含pool_size字段")
        
        # 创建多个数据库连接
        connections = []
        conn_ids = []
        for _ in range(5):
            conn_id, conn = get_db_connection()
            self.assertIsNotNone(conn, "获取的数据库连接不应为空")
            self.assertIsNotNone(conn_id, "连接ID不应为空")
            connections.append(conn)
            conn_ids.append(conn_id)
        
        # 验证连接池状态已更新
        current_stats = get_connection_stats()
        self.assertEqual(current_stats['active_connections'], 5, "活动连接数应为5")
        
        # 释放所有连接
        for i, (conn_id, conn) in enumerate(zip(conn_ids, connections)):
            pool.release_connection(conn_id, conn)
        
        # 验证连接已释放回池中
        after_release_stats = get_connection_stats()
        self.assertEqual(after_release_stats['active_connections'], 0, "释放后活动连接数应为0")
        self.assertGreaterEqual(after_release_stats['available_connections'], 5, "可用连接数应至少为5")
        
        # 关闭所有连接
        result = close_all_connections()
        self.assertTrue(result, "关闭所有连接应成功")
        
        # 验证连接池已清空
        final_stats = get_connection_stats()
        self.assertEqual(final_stats['pool_size'], 0, "关闭后连接池大小应为0")
        self.assertEqual(final_stats['active_connections'], 0, "关闭后活动连接数应为0")
        self.assertEqual(final_stats['available_connections'], 0, "关闭后可用连接数应为0")
    
    def test_thread_manager(self):
        """测试线程管理器能否正确管理线程"""
        # 创建一个测试线程
        def test_task():
            while not thread_manager.should_stop():
                time.sleep(0.1)
        
        # 获取线程管理器
        thread_manager = get_thread_manager("test_thread")
        # 启动线程
        thread_manager.start(target=test_task)
        # 验证线程是否正在运行
        self.assertTrue(thread_manager.is_running(), "测试线程未正常启动")
        
        # 停止线程
        result = thread_manager.stop()
        # 验证线程是否已停止
        self.assertTrue(result, "测试线程未能正常停止")
        self.assertFalse(thread_manager.is_running(), "测试线程仍在运行")
    
    def test_resource_leak(self):
        """测试资源泄漏检测"""
        # 记录初始进程资源使用情况
        process = psutil.Process(os.getpid())
        initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        initial_threads = threading.active_count()
        
        # 执行可能导致资源泄漏的操作
        # 1. 创建多个线程但不停止
        thread_managers = []
        for i in range(5):
            tm = get_thread_manager(f"leak_test_{i}")
            tm.start(target=lambda: time.sleep(10))
            thread_managers.append(tm)
        
        # 2. 创建多个数据库连接但不关闭
        connections = [get_db_connection() for _ in range(5)]
        # 解包连接ID和连接对象
        conn_ids = [conn_id for conn_id, _ in connections]
        conn_objects = [conn for _, conn in connections]
        
        # 正确清理资源
        for tm in thread_managers:
            tm.stop()
        
        # 使用连接池释放连接
        pool = get_connection_pool()
        for conn_id, conn in zip(conn_ids, conn_objects):
            pool.release_connection(conn_id, conn)
        
        # 等待一段时间，确保资源已释放
        time.sleep(2)
        
        # 检查资源是否有泄漏
        current_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        current_threads = threading.active_count()
        
        # 验证文件描述符数量是否恢复
        if hasattr(process, 'num_fds'):
            self.assertLessEqual(current_fds, initial_fds + 3, f"文件描述符泄漏: {initial_fds} -> {current_fds}")
        
        # 验证线程数量是否恢复
        self.assertLessEqual(current_threads, initial_threads + 2, f"线程泄漏: {initial_threads} -> {current_threads}")
    
    def test_cleanup_function(self):
        """测试清理函数能否正确清理所有资源"""
        # 启动多个服务
        start_auto_backup()
        start_resource_monitoring()
        
        # 创建一些测试线程
        for i in range(3):
            tm = get_thread_manager(f"test_cleanup_{i}")
            tm.start(target=lambda: time.sleep(30))
        
        # 等待一段时间，确保所有服务都已启动
        time.sleep(2)
        
        # 执行清理函数
        cleanup()
        
        # 等待一段时间，确保所有资源都已释放
        time.sleep(2)
        
        # 验证所有线程是否已停止
        backup_service = get_backup_service()
        self.assertFalse(backup_service.thread_manager.is_running(), "备份服务线程仍在运行")
        
        # 验证自定义线程是否已停止
        for i in range(3):
            tm = get_thread_manager(f"test_cleanup_{i}")
            self.assertFalse(tm.is_running(), f"测试线程 {i} 仍在运行")

if __name__ == '__main__':
    unittest.main()