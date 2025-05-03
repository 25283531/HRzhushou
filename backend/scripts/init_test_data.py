import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db import get_db_connection
from backend.models.salary_items import create_tables

def init_test_data():
    """初始化测试数据"""
    print("开始初始化测试数据...")
    
    # 确保表已创建
    create_tables()
    
    # 获取数据库连接
    _, conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 清空现有数据
        cursor.execute('DELETE FROM rule_salary_items')
        cursor.execute('DELETE FROM salary_items')
        cursor.execute('DELETE FROM matching_rules')
        
        # 插入薪酬项测试数据
        salary_items = [
            {
                'name': '基本工资',
                'code': 'BASE_SALARY',
                'type': 'income',
                'description': '员工的基本工资',
                'calculation_formula': None,
                'is_fixed': True,
                'default_value': 5000.00
            },
            {
                'name': '绩效奖金',
                'code': 'PERFORMANCE_BONUS',
                'type': 'income',
                'description': '根据绩效评估结果计算的奖金',
                'calculation_formula': 'base_salary * performance_rate',
                'is_fixed': False,
                'default_value': 0.00
            },
            {
                'name': '交通补贴',
                'code': 'TRANSPORT_ALLOWANCE',
                'type': 'income',
                'description': '每月固定的交通补贴',
                'calculation_formula': None,
                'is_fixed': True,
                'default_value': 300.00
            },
            {
                'name': '餐饮补贴',
                'code': 'MEAL_ALLOWANCE',
                'type': 'income',
                'description': '每月固定的餐饮补贴',
                'calculation_formula': None,
                'is_fixed': True,
                'default_value': 400.00
            },
            {
                'name': '加班工资',
                'code': 'OVERTIME_PAY',
                'type': 'income',
                'description': '加班费计算',
                'calculation_formula': '(base_salary / 21.75 / 8) * 1.5 * overtime_hours',
                'is_fixed': False,
                'default_value': 0.00
            }
        ]
        
        # 插入薪酬项并记录ID
        item_ids = {}
        for item in salary_items:
            cursor.execute('''
            INSERT INTO salary_items (name, code, type, description, calculation_formula, is_fixed, default_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item['name'], item['code'], item['type'], item['description'],
                  item['calculation_formula'], item['is_fixed'], item['default_value']))
            item_ids[item['code']] = cursor.lastrowid
        
        # 插入匹配规则测试数据
        matching_rules = [
            {
                'name': '标准薪资包',
                'description': '适用于普通员工的标准薪资组合',
                'conditions': json.dumps({
                    'position_level': ['P1', 'P2'],
                    'department': ['*']
                }),
                'priority': 1,
                'is_active': True,
                'salary_items': [
                    item_ids['BASE_SALARY'],
                    item_ids['TRANSPORT_ALLOWANCE'],
                    item_ids['MEAL_ALLOWANCE']
                ]
            },
            {
                'name': '绩效奖金规则',
                'description': '绩效达标员工的奖金计算规则',
                'conditions': json.dumps({
                    'performance_score': {'min': 3.5},
                    'employment_status': 'FULL_TIME'
                }),
                'priority': 2,
                'is_active': True,
                'salary_items': [
                    item_ids['PERFORMANCE_BONUS']
                ]
            },
            {
                'name': '加班工资规则',
                'description': '加班工资计算规则',
                'conditions': json.dumps({
                    'overtime_hours': {'min': 1}
                }),
                'priority': 3,
                'is_active': True,
                'salary_items': [
                    item_ids['OVERTIME_PAY']
                ]
            }
        ]
        
        # 插入匹配规则
        for rule in matching_rules:
            cursor.execute('''
            INSERT INTO matching_rules (name, description, conditions, priority, is_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (rule['name'], rule['description'], rule['conditions'],
                  rule['priority'], rule['is_active']))
            rule_id = cursor.lastrowid
            
            # 插入规则-薪酬项关联
            for item_id in rule['salary_items']:
                cursor.execute('''
                INSERT INTO rule_salary_items (rule_id, item_id)
                VALUES (?, ?)
                ''', (rule_id, item_id))
        
        conn.commit()
        print("测试数据初始化完成！")
        
        # 打印统计信息
        cursor.execute('SELECT COUNT(*) as count FROM salary_items')
        salary_items_count = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM matching_rules')
        rules_count = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM rule_salary_items')
        relations_count = cursor.fetchone()['count']
        
        print(f"\n统计信息:")
        print(f"- 薪酬项数量: {salary_items_count}")
        print(f"- 匹配规则数量: {rules_count}")
        print(f"- 规则-薪酬项关联数量: {relations_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"初始化测试数据失败: {str(e)}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    init_test_data() 