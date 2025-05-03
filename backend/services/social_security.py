import json
from datetime import datetime, timedelta
import calendar
from backend.database.models import Employee
from backend.database.db import execute_query, get_current_time

class SocialSecurityService:
    """社保处理服务类，处理社保计算和管理"""
    
    def __init__(self):
        pass
    
    def get_insurance_items(self):
        """获取所有社保项
        
        Returns:
            社保项列表
        """
        query = 'SELECT * FROM insurance_items ORDER BY name'
        return execute_query(query)
    
    def get_insurance_groups(self):
        """获取所有社保组
        
        Returns:
            社保组列表
        """
        query = 'SELECT * FROM insurance_groups ORDER BY name'
        return execute_query(query)
    
    def get_employee_insurance_group(self, employee_id):
        """获取员工所属的社保组
        
        Args:
            employee_id: 员工ID
            
        Returns:
            社保组信息
        """
        # 这里假设员工表中有insurance_group_id字段，如果没有，需要从其他地方获取
        query = '''
        SELECT ig.* FROM insurance_groups ig
        JOIN employees e ON e.insurance_group_id = ig.id
        WHERE e.id = ?
        '''
        
        result = execute_query(query, (employee_id,), one=True)
        
        # 如果没有找到社保组，使用默认社保组
        if not result:
            # 获取默认社保组（这里简单地取第一个）
            groups = self.get_insurance_groups()
            if groups:
                return groups[0]
            else:
                return None
        
        return result
    
    def calculate_employee_insurance(self, employee_id, month):
        """计算员工社保
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            
        Returns:
            社保计算结果
        """
        # 获取员工信息
        employee = Employee.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"找不到ID为{employee_id}的员工")
        
        # 获取员工所属的社保组
        insurance_group = self.get_employee_insurance_group(employee_id)
        if not insurance_group:
            return {
                'personal_total': 0,
                'company_total': 0,
                'items': []
            }
        
        # 解析社保组中的社保项
        items_json = insurance_group['items']
        item_ids = json.loads(items_json) if isinstance(items_json, str) else items_json
        
        # 获取社保基数
        base_amount = insurance_group['base_amount']
        
        # 计算该月的天数
        year, month_num = map(int, month.split('-'))
        total_days = calendar.monthrange(year, month_num)[1]
        
        # 检查员工是否在该月中途入职或离职
        is_partial_month = False
        work_days = total_days
        
        # 检查入职日期
        if employee['entry_date']:
            entry_date = datetime.strptime(employee['entry_date'], '%Y-%m-%d')
            month_start = datetime(year, month_num, 1)
            if entry_date.year == year and entry_date.month == month_num:
                is_partial_month = True
                # 计算实际工作天数（从入职日期到月底）
                work_days = total_days - entry_date.day + 1
        
        # 检查离职日期
        if employee['leave_date']:
            leave_date = datetime.strptime(employee['leave_date'], '%Y-%m-%d')
            month_end = datetime(year, month_num, total_days)
            if leave_date.year == year and leave_date.month == month_num:
                is_partial_month = True
                # 如果已经考虑了入职日期，需要重新计算工作天数
                if work_days < total_days:
                    # 从入职日期到离职日期
                    entry_day = datetime(year, month_num, total_days - work_days + 1)
                    work_days = (leave_date - entry_day).days + 1
                else:
                    # 从月初到离职日期
                    work_days = leave_date.day
        
        # 计算社保比例
        ratio = work_days / total_days if is_partial_month else 1.0
        
        # 获取社保项详情并计算
        items_result = []
        personal_total = 0
        company_total = 0
        
        for item_id in item_ids:
            # 获取社保项信息
            query = 'SELECT * FROM insurance_items WHERE id = ?'
            item = execute_query(query, (item_id,), one=True)
            
            if item:
                # 计算个人和公司缴纳部分
                personal_amount = base_amount * item['personal_rate'] * ratio
                company_amount = base_amount * item['company_rate'] * ratio
                
                items_result.append({
                    'id': item['id'],
                    'name': item['name'],
                    'personal_rate': item['personal_rate'],
                    'company_rate': item['company_rate'],
                    'personal_amount': personal_amount,
                    'company_amount': company_amount
                })
                
                personal_total += personal_amount
                company_total += company_amount
        
        return {
            'personal_total': personal_total,
            'company_total': company_total,
            'items': items_result,
            'base_amount': base_amount,
            'is_partial_month': is_partial_month,
            'work_days': work_days,
            'total_days': total_days,
            'ratio': ratio
        }
    
    def calculate_social_security(self, data):
        """计算社保
        
        Args:
            data: 包含计算参数的字典，必须包含month字段，可选包含employee_id字段
            
        Returns:
            计算结果列表
        """
        month = data.get('month')
        if not month:
            raise ValueError("缺少必要参数: month")
        
        employee_id = data.get('employee_id')
        
        # 获取员工列表
        if employee_id:
            employees = [Employee.get_by_id(employee_id)]
            if not employees[0]:
                raise ValueError(f"找不到ID为{employee_id}的员工")
        else:
            employees = Employee.get_all()
        
        results = []
        for employee in employees:
            # 计算社保
            insurance_result = self.calculate_employee_insurance(employee['id'], month)
            
            # 添加员工信息到结果中
            insurance_result['employee'] = {
                'id': employee['id'],
                'name': employee['name'],
                'employee_id': employee['employee_id'],
                'department': employee['department'],
                'position': employee['position']
            }
            
            results.append(insurance_result)
        
        return results