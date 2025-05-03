import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.models.position_levels import create_tables as create_position_level_tables
from backend.models.position_levels import (
    create_level_type,
    create_position_level
)

def init_position_level_data():
    """初始化职位职级测试数据"""
    print("初始化职位职级测试数据...")
    
    # 创建表
    create_position_level_tables()
    
    # 创建管理序列
    management_type = {
        'name': '管理序列',
        'code': 'M',
        'description': '管理岗位序列',
        'is_active': True
    }
    management_type_id = create_level_type(management_type)
    
    # 创建管理序列职级
    management_levels = [
        {
            'type_id': management_type_id,
            'name': '总经理',
            'code': 'M6',
            'level': 6,
            'description': '公司最高管理层',
            'is_active': True
        },
        {
            'type_id': management_type_id,
            'name': '副总经理',
            'code': 'M5',
            'level': 5,
            'description': '分管副总',
            'is_active': True
        },
        {
            'type_id': management_type_id,
            'name': '部门总监',
            'code': 'M4',
            'level': 4,
            'description': '部门最高负责人',
            'is_active': True
        },
        {
            'type_id': management_type_id,
            'name': '部门经理',
            'code': 'M3',
            'level': 3,
            'description': '部门管理者',
            'is_active': True
        },
        {
            'type_id': management_type_id,
            'name': '主管',
            'code': 'M2',
            'level': 2,
            'description': '团队负责人',
            'is_active': True
        },
        {
            'type_id': management_type_id,
            'name': '组长',
            'code': 'M1',
            'level': 1,
            'description': '小组负责人',
            'is_active': True
        }
    ]
    
    for level in management_levels:
        create_position_level(level)
    
    # 创建专业序列
    professional_type = {
        'name': '专业序列',
        'code': 'P',
        'description': '专业技术岗位序列',
        'is_active': True
    }
    professional_type_id = create_level_type(professional_type)
    
    # 创建专业序列职级
    professional_levels = [
        {
            'type_id': professional_type_id,
            'name': '专家',
            'code': 'P6',
            'level': 6,
            'description': '领域专家',
            'is_active': True
        },
        {
            'type_id': professional_type_id,
            'name': '高级专家',
            'code': 'P5',
            'level': 5,
            'description': '高级技术专家',
            'is_active': True
        },
        {
            'type_id': professional_type_id,
            'name': '资深工程师',
            'code': 'P4',
            'level': 4,
            'description': '资深技术人员',
            'is_active': True
        },
        {
            'type_id': professional_type_id,
            'name': '高级工程师',
            'code': 'P3',
            'level': 3,
            'description': '高级技术人员',
            'is_active': True
        },
        {
            'type_id': professional_type_id,
            'name': '中级工程师',
            'code': 'P2',
            'level': 2,
            'description': '中级技术人员',
            'is_active': True
        },
        {
            'type_id': professional_type_id,
            'name': '初级工程师',
            'code': 'P1',
            'level': 1,
            'description': '初级技术人员',
            'is_active': True
        }
    ]
    
    for level in professional_levels:
        create_position_level(level)
    
    print("职位职级测试数据初始化完成！")

if __name__ == '__main__':
    init_position_level_data() 