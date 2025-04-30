import json
from datetime import datetime
from database.models import Employee, PositionChange
from database.db import get_current_time

class EmployeeService:
    """员工信息服务类，处理员工基本信息和职位变动"""
    
    def __init__(self):
        pass
    
    def get_all_employees(self):
        """获取所有员工信息
        
        Returns:
            员工信息列表
        """
        return Employee.get_all()
    
    def get_employee_by_id(self, employee_id):
        """根据ID获取员工信息
        
        Args:
            employee_id: 员工ID
            
        Returns:
            员工信息
        """
        return Employee.get_by_id(employee_id)
    
    def add_employee(self, employee_data):
        """添加员工
        
        Args:
            employee_data: 员工数据
            
        Returns:
            新增员工的ID
        """
        # 验证必要字段
        if not employee_data.get('name'):
            raise ValueError("员工姓名不能为空")
        
        if not employee_data.get('employee_id') and not employee_data.get('id_card'):
            raise ValueError("员工工号和身份证号至少需要提供一项")
        
        # 创建员工记录
        return Employee.create(employee_data)
    
    def update_employee(self, employee_id, employee_data):
        """更新员工信息
        
        Args:
            employee_id: 员工ID
            employee_data: 更新的员工数据
            
        Returns:
            更新后的员工信息
        """
        # 验证员工是否存在
        employee = Employee.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"找不到ID为{employee_id}的员工")
        
        # 更新员工记录
        return Employee.update(employee_id, employee_data)
    
    def delete_employee(self, employee_id):
        """删除员工
        
        Args:
            employee_id: 员工ID
            
        Returns:
            是否成功删除
        """
        # 验证员工是否存在
        employee = Employee.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"找不到ID为{employee_id}的员工")
        
        # 删除员工记录
        return Employee.delete(employee_id)
    
    def add_position_change(self, change_data):
        """添加职位变动记录
        
        Args:
            change_data: 职位变动数据，包含employee_id, old_position, new_position, 
                        old_salary, new_salary, effective_date
            
        Returns:
            新增记录的ID
        """
        # 验证必要字段
        required_fields = ['employee_id', 'new_position', 'new_salary', 'effective_date']
        for field in required_fields:
            if field not in change_data or not change_data[field]:
                raise ValueError(f"缺少必要字段: {field}")
        
        # 验证员工是否存在
        employee = Employee.get_by_id(change_data['employee_id'])
        if not employee:
            raise ValueError(f"找不到ID为{change_data['employee_id']}的员工")
        
        # 如果没有提供旧职位和旧薪资，则从员工信息中获取
        if 'old_position' not in change_data or not change_data['old_position']:
            change_data['old_position'] = employee['position']
        
        if 'old_salary' not in change_data or not change_data['old_salary']:
            # 这里假设员工表中有salary字段，如果没有，需要从其他地方获取
            # 或者要求必须提供old_salary
            change_data['old_salary'] = 0
        
        # 创建职位变动记录
        position_change_id = PositionChange.create(change_data)
        
        # 更新员工信息中的职位
        Employee.update(change_data['employee_id'], {
            'position': change_data['new_position']
        })
        
        return position_change_id
    
    def get_position_changes(self, employee_id=None, month=None):
        """获取职位变动记录
        
        Args:
            employee_id: 员工ID，如果为None则获取所有员工的记录
            month: 月份，格式为YYYY-MM，如果为None则获取所有记录
            
        Returns:
            职位变动记录列表
        """
        if employee_id and month:
            # 获取指定员工在指定月份的职位变动记录
            position_changes = PositionChange.get_by_employee(employee_id)
            return [pc for pc in position_changes if pc['effective_date'].startswith(month)]
        elif employee_id:
            # 获取指定员工的所有职位变动记录
            return PositionChange.get_by_employee(employee_id)
        elif month:
            # 获取指定月份的所有职位变动记录
            return PositionChange.get_by_month(month)
        else:
            # 获取所有职位变动记录
            from database.db import execute_query
            return execute_query('SELECT * FROM position_changes ORDER BY effective_date DESC')
    
    def calculate_salary_by_position_change(self, employee_id, month, total_days):
        """根据职位变动计算薪资比例
        
        当员工在同一个月内有职位变动时，需要按比例计算不同职位的薪资
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            total_days: 该月总天数
            
        Returns:
            包含不同职位薪资比例的字典
        """
        # 获取该月的职位变动记录
        position_changes = self.get_position_changes(employee_id, month)
        
        if not position_changes:
            # 没有职位变动，返回默认薪资信息
            employee = Employee.get_by_id(employee_id)
            return [{
                'position': employee['position'],
                'salary': 0,  # 这里需要从其他地方获取薪资信息
                'days': total_days,
                'ratio': 1.0
            }]
        
        # 按生效日期排序
        position_changes.sort(key=lambda x: x['effective_date'])
        
        # 计算每个职位的工作天数和薪资比例
        result = []
        month_start = f"{month}-01"
        
        # 确定月末日期
        year, month_num = map(int, month.split('-'))
        if month_num == 12:
            next_month = f"{year+1}-01-01"
        else:
            next_month = f"{year}-{month_num+1:02d}-01"
        
        # 计算每段时间的天数和比例
        prev_date = month_start
        prev_position = position_changes[0]['old_position']
        prev_salary = position_changes[0]['old_salary']
        
        for change in position_changes:
            if change['effective_date'] < month_start or change['effective_date'] >= next_month:
                continue
            
            # 计算当前职位的工作天数
            start_date = datetime.strptime(prev_date, '%Y-%m-%d')
            end_date = datetime.strptime(change['effective_date'], '%Y-%m-%d')
            days = (end_date - start_date).days
            
            if days > 0:
                result.append({
                    'position': prev_position,
                    'salary': prev_salary,
                    'days': days,
                    'ratio': days / total_days
                })
            
            prev_date = change['effective_date']
            prev_position = change['new_position']
            prev_salary = change['new_salary']
        
        # 添加最后一段时间
        start_date = datetime.strptime(prev_date, '%Y-%m-%d')
        end_date = datetime.strptime(next_month, '%Y-%m-%d')
        days = (end_date - start_date).days
        
        if days > 0:
            result.append({
                'position': prev_position,
                'salary': prev_salary,
                'days': days,
                'ratio': days / total_days
            })
        
        return result