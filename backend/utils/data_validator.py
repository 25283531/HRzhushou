import re
from datetime import datetime
from .date_parser import parse_date

class DataValidator:
    """数据验证工具类，用于验证导入的数据格式和内容的正确性"""
    
    @staticmethod
    def validate_employee_data(data):
        """验证员工数据
        
        Args:
            data: 员工数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        if not data.get('name'):
            return False, "员工姓名不能为空"
        
        if not data.get('employee_id') and not data.get('id_card'):
            return False, "员工工号和身份证号至少需要提供一项"
        
        # 验证身份证号格式
        if data.get('id_card'):
            id_card = data.get('id_card')
            if not DataValidator.is_valid_id_card(id_card):
                return False, f"身份证号格式不正确: {id_card}"
        
        # 验证日期格式
        date_fields = ['entry_date', 'leave_date']
        for field in date_fields:
            if data.get(field):
                parsed_date = parse_date(data.get(field))
                if not parsed_date:
                    return False, f"{field}日期格式不正确: {data.get(field)}"
        
        return True, ""
    
    @staticmethod
    def validate_attendance_data(data):
        """验证考勤数据
        
        Args:
            data: 考勤数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        if not data.get('employee_id'):
            return False, "员工ID不能为空"
        
        if not data.get('date'):
            return False, "考勤日期不能为空"
        
        # 验证日期格式
        parsed_date = parse_date(data.get('date'))
        if not parsed_date:
            return False, f"日期格式不正确: {data.get('date')}"
        
        # 验证数值字段
        numeric_fields = ['work_hours', 'late_minutes', 'early_leave_minutes', 'overtime_hours', 'absence_days']
        for field in numeric_fields:
            if field in data and data.get(field) is not None:
                try:
                    value = float(data.get(field))
                    if value < 0:
                        return False, f"{field}不能为负数: {value}"
                except ValueError:
                    return False, f"{field}必须是数字: {data.get(field)}"
        
        return True, ""
    
    @staticmethod
    def validate_salary_group_data(data):
        """验证薪资组数据
        
        Args:
            data: 薪资组数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        if not data.get('name'):
            return False, "薪资组名称不能为空"
        
        return True, ""
    
    @staticmethod
    def validate_insurance_item_data(data):
        """验证社保项数据
        
        Args:
            data: 社保项数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        if not data.get('name'):
            return False, "社保项名称不能为空"
        
        # 验证比例字段
        rate_fields = ['personal_rate', 'company_rate']
        for field in rate_fields:
            if field in data and data.get(field) is not None:
                try:
                    value = float(data.get(field))
                    if value < 0 or value > 1:
                        return False, f"{field}必须在0-1之间: {value}"
                except ValueError:
                    return False, f"{field}必须是数字: {data.get(field)}"
        
        return True, ""
    
    @staticmethod
    def validate_insurance_group_data(data):
        """验证社保组数据
        
        Args:
            data: 社保组数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        if not data.get('name'):
            return False, "社保组名称不能为空"
        
        # 验证基数字段
        if data.get('base_amount') is not None:
            try:
                value = float(data.get('base_amount'))
                if value < 0:
                    return False, f"基数不能为负数: {value}"
            except ValueError:
                return False, f"基数必须是数字: {data.get('base_amount')}"
        
        # 验证社保项列表
        if data.get('items') is not None:
            if not isinstance(data.get('items'), list):
                return False, "社保项必须是列表"
        
        return True, ""
    
    @staticmethod
    def is_valid_id_card(id_card):
        """验证身份证号格式
        
        Args:
            id_card: 身份证号
            
        Returns:
            bool: 是否有效
        """
        # 简单验证18位身份证号
        if re.match(r'^\d{17}[0-9X]$', id_card):
            return True
        
        # 简单验证15位身份证号
        if re.match(r'^\d{15}$', id_card):
            return True
        
        return False
    
    @staticmethod
    def validate_position_change_data(data):
        """验证职位变动数据
        
        Args:
            data: 职位变动数据字典
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必填字段
        required_fields = ['employee_id', 'new_position', 'new_salary', 'effective_date']
        for field in required_fields:
            if not data.get(field):
                return False, f"{field}不能为空"
        
        # 验证日期格式
        parsed_date = parse_date(data.get('effective_date'))
        if not parsed_date:
            return False, f"生效日期格式不正确: {data.get('effective_date')}"
        
        # 验证薪资字段
        salary_fields = ['old_salary', 'new_salary']
        for field in salary_fields:
            if field in data and data.get(field) is not None:
                try:
                    value = float(data.get(field))
                    if value < 0:
                        return False, f"{field}不能为负数: {value}"
                except ValueError:
                    return False, f"{field}必须是数字: {data.get(field)}"
        
        return True, ""
    
    @staticmethod
    def validate_excel_mapping(mapping, required_fields):
        """验证Excel映射配置
        
        Args:
            mapping: 字段映射字典
            required_fields: 必需的字段列表
            
        Returns:
            (bool, str): 验证结果和错误信息
        """
        # 验证必需的字段映射
        for field in required_fields:
            if field not in mapping or not mapping[field]:
                return False, f"缺少必要的字段映射: {field}"
        
        return True, ""