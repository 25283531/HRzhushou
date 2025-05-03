import json
from datetime import datetime, timedelta
import calendar
from backend.database.models import SalaryRecord, Employee
from backend.database.db import get_current_time
from backend.database.models import SalaryGroup  # 假设存在 SalaryGroup 模型
from backend.services.employee import EmployeeService
from backend.services.attendance import AttendanceService
from backend.services.social_security import SocialSecurityService

class SalaryService:
    """薪资计算服务类，处理薪资计算和薪资记录管理"""
    
    def __init__(self):
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.social_security_service = SocialSecurityService()
        # 可以在这里初始化 SalaryGroup 的数据库操作，如果需要的话
    
    def calculate_salary(self, data):
        """计算薪资
        
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
            employees = [self.employee_service.get_employee_by_id(employee_id)]
            if not employees[0]:
                raise ValueError(f"找不到ID为{employee_id}的员工")
        else:
            employees = self.employee_service.get_all_employees()
        
        # 计算该月的天数
        year, month_num = map(int, month.split('-'))
        total_days = calendar.monthrange(year, month_num)[1]
        
        results = []
        for employee in employees:
            # 计算薪资
            salary_result = self._calculate_employee_salary(employee['id'], month, total_days)
            
            # 保存薪资记录
            record_id = self._save_salary_record(employee['id'], month, salary_result)
            
            # 添加员工信息到结果中
            salary_result['employee'] = {
                'id': employee['id'],
                'name': employee['name'],
                'employee_id': employee['employee_id'],
                'department': employee['department'],
                'position': employee['position']
            }
            salary_result['record_id'] = record_id
            
            results.append(salary_result)
        
        return results
    
    def _calculate_employee_salary(self, employee_id, month, total_days):
        """计算单个员工的薪资
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            total_days: 该月总天数
            
        Returns:
            薪资计算结果
        """
        # 获取员工信息
        employee = self.employee_service.get_employee_by_id(employee_id)
        
        # 获取考勤汇总数据
        attendance_summary = self.attendance_service.calculate_attendance_summary(employee_id, month)
        
        # 获取职位变动信息，计算薪资比例
        position_salary_ratios = self.employee_service.calculate_salary_by_position_change(employee_id, month, total_days)
        
        # 计算社保
        social_security = self.social_security_service.calculate_employee_insurance(employee_id, month)
        
        # 计算基本薪资（考虑职位变动）
        base_salary = sum(ps['salary'] * ps['ratio'] for ps in position_salary_ratios)
        
        # 计算考勤扣款
        attendance_deduction = self._calculate_attendance_deduction(base_salary, attendance_summary)
        
        # 计算个税
        tax = self._calculate_tax(base_salary - social_security['personal_total'] - attendance_deduction)
        
        # 计算实发工资
        actual_salary = base_salary - social_security['personal_total'] - attendance_deduction - tax
        
        # 返回计算结果
        return {
            'base_salary': base_salary,
            'attendance_deduction': attendance_deduction,
            'social_security': social_security,
            'tax': tax,
            'actual_salary': actual_salary,
            'attendance_summary': attendance_summary,
            'position_salary_ratios': position_salary_ratios,
            'details': {
                'base_salary': base_salary,
                'attendance_deduction': attendance_deduction,
                'social_security_personal': social_security['personal_total'],
                'social_security_company': social_security['company_total'],
                'tax': tax,
                'actual_salary': actual_salary
            }
        }
    
    def _calculate_attendance_deduction(self, base_salary, attendance_summary):
        """计算考勤扣款
        
        Args:
            base_salary: 基本薪资
            attendance_summary: 考勤汇总数据
            
        Returns:
            考勤扣款金额
        """
        # 这里使用简单的计算规则，实际应用中可能需要更复杂的规则
        daily_salary = base_salary / 30  # 假设每月30天
        
        # 缺勤扣款
        absence_deduction = daily_salary * attendance_summary['absence_days']
        
        # 迟到扣款（假设每分钟扣款为日薪的1/480）
        late_deduction = (daily_salary / 480) * attendance_summary['total_late_minutes']
        
        # 早退扣款（假设每分钟扣款为日薪的1/480）
        early_leave_deduction = (daily_salary / 480) * attendance_summary['total_early_leave_minutes']
        
        return absence_deduction + late_deduction + early_leave_deduction
    
    def _calculate_tax(self, taxable_income):
        """计算个人所得税
        
        Args:
            taxable_income: 应纳税所得额
            
        Returns:
            个税金额
        """
        # 个税起征点
        threshold = 5000
        
        # 如果不超过起征点，则不缴纳个税
        if taxable_income <= threshold:
            return 0
        
        # 应纳税所得额 = 工资收入 - 起征点
        taxable_amount = taxable_income - threshold
        
        # 个税税率表
        tax_rates = [
            (0, 3000, 0.03, 0),
            (3000, 12000, 0.1, 210),
            (12000, 25000, 0.2, 1410),
            (25000, 35000, 0.25, 2660),
            (35000, 55000, 0.3, 4410),
            (55000, 80000, 0.35, 7160),
            (80000, float('inf'), 0.45, 15160)
        ]
        
        # 计算个税
        for lower, upper, rate, quick_deduction in tax_rates:
            if lower < taxable_amount <= upper:
                return taxable_amount * rate - quick_deduction
        
        # 如果应纳税所得额超过最高档
        return taxable_amount * 0.45 - 15160

    def create_salary_group(self, group_data):
        """创建新的薪资组

        Args:
            group_data: 包含薪资组信息的字典，例如 {'name': 'Group Name', 'description': '描述', 'formula': '公式'}

        Returns:
            创建的薪资组对象或其ID
        """
        # 验证输入数据
        name = group_data.get('name')
        if not name:
            raise ValueError("薪资组名称不能为空")

        # 检查名称是否已存在
        from backend.database.db import execute_query
        existing_group = execute_query('SELECT * FROM salary_groups WHERE name = ?', (name,), one=True)
        if existing_group:
            raise ValueError(f"名称为 '{name}' 的薪资组已存在")

        # 准备数据
        data = {
            'name': name,
            'description': group_data.get('description', ''),
            'formula': json.dumps(group_data.get('formula', {})) if isinstance(group_data.get('formula'), dict) else group_data.get('formula', '')
        }
        
        # 创建薪资组记录
        group_id = SalaryGroup.create(data)
        
        # 获取创建的薪资组信息
        new_group = SalaryGroup.get_by_id(group_id)
        return new_group
    
    def _save_salary_record(self, employee_id, month, salary_result):
        """保存薪资记录
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            salary_result: 薪资计算结果
            
        Returns:
            记录ID
        """
        # 检查是否已存在记录
        existing_record = SalaryRecord.get_by_employee_and_month(employee_id, month)
        
        record_data = {
            'employee_id': employee_id,
            'month': month,
            'base_salary': salary_result['base_salary'],
            'actual_salary': salary_result['actual_salary'],
            'deductions': salary_result['attendance_deduction'],
            'insurance': salary_result['social_security']['personal_total'],
            'tax': salary_result['tax'],
            'details': salary_result['details']
        }
        
        if existing_record:
            # 更新现有记录
            SalaryRecord.update(existing_record['id'], record_data)
            return existing_record['id']
        else:
            # 创建新记录
            return SalaryRecord.create(record_data)
    
    def get_salary_history(self, month=None, employee_id=None):
        """获取薪资历史记录
        
        Args:
            month: 月份，格式为YYYY-MM，如果为None则获取所有记录
            employee_id: 员工ID，如果为None则获取所有员工的记录
            
        Returns:
            薪资记录列表
        """
        if month and employee_id:
            # 获取指定员工在指定月份的薪资记录
            record = SalaryRecord.get_by_employee_and_month(employee_id, month)
            return [record] if record else []
        elif month:
            # 获取指定月份的所有薪资记录
            return SalaryRecord.get_by_month(month)
        elif employee_id:
            # 获取指定员工的所有薪资记录
            from database.db import execute_query
            return execute_query('SELECT * FROM salary_records WHERE employee_id = ? ORDER BY month DESC', (employee_id,))
        else:
            # 获取所有薪资记录
            from database.db import execute_query
            return execute_query('SELECT * FROM salary_records ORDER BY month DESC, employee_id')
    
    def analyze_salary_cost(self, month):
        """分析薪资成本
        
        Args:
            month: 月份，格式为YYYY-MM
            
        Returns:
            薪资成本分析结果
        """
        # 获取该月的所有薪资记录
        salary_records = self.get_salary_history(month)
        
        if not salary_records:
            return {
                'total_cost': 0,
                'salary_cost': 0,
                'insurance_cost': 0,
                'department_costs': [],
                'position_costs': []
            }
        
        # 初始化统计数据
        total_salary = 0
        total_insurance = 0
        department_costs = {}
        position_costs = {}
        
        # 统计各项成本
        for record in salary_records:
            # 获取员工信息
            employee = self.employee_service.get_employee_by_id(record['employee_id'])
            
            # 计算薪资成本
            salary_cost = record['base_salary']
            total_salary += salary_cost
            
            # 计算社保成本（公司部分）
            details = json.loads(record['details']) if isinstance(record['details'], str) else record['details']
            insurance_cost = details.get('social_security_company', 0)
            total_insurance += insurance_cost
            
            # 按部门统计
            department = employee['department']
            if department not in department_costs:
                department_costs[department] = {
                    'department': department,
                    'count': 0,
                    'salary_cost': 0,
                    'insurance_cost': 0,
                    'total_cost': 0
                }
            
            department_costs[department]['count'] += 1
            department_costs[department]['salary_cost'] += salary_cost
            department_costs[department]['insurance_cost'] += insurance_cost
            department_costs[department]['total_cost'] += salary_cost + insurance_cost
            
            # 按职位统计
            position = employee['position']
            if position not in position_costs:
                position_costs[position] = {
                    'position': position,
                    'count': 0,
                    'salary_cost': 0,
                    'insurance_cost': 0,
                    'total_cost': 0
                }
            
            position_costs[position]['count'] += 1
            position_costs[position]['salary_cost'] += salary_cost
            position_costs[position]['insurance_cost'] += insurance_cost
            position_costs[position]['total_cost'] += salary_cost + insurance_cost
        
        # 计算总成本
        total_cost = total_salary + total_insurance
        
        # 返回分析结果
        return {
            'total_cost': total_cost,
            'salary_cost': total_salary,
            'insurance_cost': total_insurance,
            'department_costs': list(department_costs.values()),
            'position_costs': list(position_costs.values())
        }