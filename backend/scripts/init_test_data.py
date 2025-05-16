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
        cursor.execute('DELETE FROM employees')
        
        # 插入员工测试数据
        employees = [
            {
                'name': '张三', 'employee_number': 'E1001', 'id_card_number': '110101199001010011', 'department_level1': '技术部', 'department_level2': '开发组', 'position': '开发工程师', 'entry_date': '2022-01-10', 'salary_group': 1, 'social_security_group': 1, 'bank_account': '6222021001000111111', 'phone': '13800000001', 'remarks': '优秀员工', 'status': '实习'
            },
            {
                'name': '李四', 'employee_number': 'E1002', 'id_card_number': '110101199202020022', 'department_level1': '技术部', 'department_level2': '测试组', 'position': '测试工程师', 'entry_date': '2021-03-15', 'salary_group': 2, 'social_security_group': 2, 'bank_account': '6222021001000222222', 'phone': '13800000002', 'remarks': '测试能力强', 'status': '正式'
            },
            {
                'name': '王五', 'employee_number': 'E1003', 'id_card_number': '110101199303030033', 'department_level1': '人事部', 'department_level2': '招聘组', 'position': '招聘专员', 'entry_date': '2020-07-01', 'salary_group': 1, 'social_security_group': 1, 'bank_account': '6222021001000333333', 'phone': '13800000003', 'remarks': '负责招聘', 'status': '派遣'
            },
            {
                'name': '赵六', 'employee_number': 'E1004', 'id_card_number': '110101199404040044', 'department_level1': '财务部', 'department_level2': '财务组', 'position': '会计', 'entry_date': '2019-11-20', 'salary_group': 2, 'social_security_group': 2, 'bank_account': '6222021001000444444', 'phone': '13800000004', 'remarks': '财务管理', 'status': '正式'
            },
            {
                'name': '孙七', 'employee_number': 'E1005', 'id_card_number': '110101199505050055', 'department_level1': '市场部', 'department_level2': '市场组', 'position': '市场专员', 'entry_date': '2023-02-18', 'salary_group': 3, 'social_security_group': 1, 'bank_account': '6222021001000555555', 'phone': '13800000005', 'remarks': '市场推广', 'status': '临时'
            },
            {
                'name': '周八', 'employee_number': 'E1006', 'id_card_number': '110101199606060066', 'department_level1': '销售部', 'department_level2': '销售组', 'position': '销售经理', 'entry_date': '2018-05-30', 'salary_group': 3, 'social_security_group': 2, 'bank_account': '6222021001000666666', 'phone': '13800000006', 'remarks': '销售业绩突出', 'status': '正式'
            },
            {
                'name': '吴九', 'employee_number': 'E1007', 'id_card_number': '110101199707070077', 'department_level1': '技术部', 'department_level2': '运维组', 'position': '运维工程师', 'entry_date': '2022-09-12', 'salary_group': 1, 'social_security_group': 1, 'bank_account': '6222021001000777777', 'phone': '13800000007', 'remarks': '负责系统运维', 'status': '派遣'
            },
            {
                'name': '郑十', 'employee_number': 'E1008', 'id_card_number': '110101199808080088', 'department_level1': '人事部', 'department_level2': '培训组', 'position': '培训专员', 'entry_date': '2021-12-01', 'salary_group': 2, 'social_security_group': 2, 'bank_account': '6222021001000888888', 'phone': '13800000008', 'remarks': '负责员工培训', 'status': '实习'
            },
            {
                'name': '钱十一', 'employee_number': 'E1009', 'id_card_number': '110101199909090099', 'department_level1': '市场部', 'department_level2': '市场组', 'position': '市场经理', 'entry_date': '2017-08-25', 'salary_group': 3, 'social_security_group': 1, 'bank_account': '6222021001000999999', 'phone': '13800000009', 'remarks': '市场管理', 'status': '正式'
            },
            {
                'name': '冯十二', 'employee_number': 'E1010', 'id_card_number': '110101200001010010', 'department_level1': '销售部', 'department_level2': '销售组', 'position': '销售助理', 'entry_date': '2023-04-10', 'salary_group': 1, 'social_security_group': 2, 'bank_account': '6222021001001010101', 'phone': '13800000010', 'remarks': '协助销售', 'status': '临时'
            },
            {
                'name': '陈十三', 'employee_number': 'E1011', 'id_card_number': '110101200102020011', 'department_level1': '技术部', 'department_level2': '开发组', 'position': '高级开发', 'entry_date': '2016-10-15', 'salary_group': 3, 'social_security_group': 2, 'bank_account': '6222021001001111111', 'phone': '13800000011', 'remarks': '技术骨干', 'status': '正式'
            }
        ]
        for emp in employees:
            cursor.execute('''
                INSERT INTO employees (name, employee_number, id_card_number, department_level1, department_level2, position, entry_date, salary_group, social_security_group, bank_account, phone, remarks, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                emp['name'], emp['employee_number'], emp['id_card_number'], emp['department_level1'], emp['department_level2'], emp['position'], emp['entry_date'], emp['salary_group'], emp['social_security_group'], emp['bank_account'], emp['phone'], emp['remarks'], emp['status']
            ))

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