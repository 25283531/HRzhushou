import os
import pandas as pd
import json
from datetime import datetime
from backend.database.models import Attendance, Employee
from backend.database.db import get_current_time

class AttendanceService:
    """考勤数据服务类，处理考勤数据的导入和查询"""
    
    def __init__(self):
        pass
    
    def import_attendance_data(self, file, mapping_json):
        """导入考勤数据
        
        Args:
            file: 上传的文件对象
            mapping_json: 字段映射JSON字符串，指定Excel列与系统字段的对应关系
            
        Returns:
            导入的记录数量
        """
        # 保存上传的文件
        temp_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp', file.filename)
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        file.save(temp_file_path)
        
        # 解析字段映射
        mapping = json.loads(mapping_json)
        
        # 根据文件扩展名选择不同的读取方法
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext == '.xlsx' or file_ext == '.xls':
            df = pd.read_excel(temp_file_path)
        elif file_ext == '.csv':
            df = pd.read_csv(temp_file_path)
        else:
            os.remove(temp_file_path)  # 清理临时文件
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        # 验证必要的字段映射
        required_fields = ['employee_id', 'date']
        for field in required_fields:
            if field not in mapping or not mapping[field]:
                os.remove(temp_file_path)  # 清理临时文件
                raise ValueError(f"缺少必要的字段映射: {field}")
        
        # 处理数据并导入
        imported_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # 获取员工ID
                employee_identifier = str(row[mapping['employee_id']])
                # 查找员工
                employees = Employee.get_all()
                employee = next((e for e in employees if str(e['employee_id']) == employee_identifier or str(e['id_card']) == employee_identifier), None)
                
                if not employee:
                    errors.append(f"找不到员工: {employee_identifier}")
                    continue
                
                # 解析日期
                date_str = row[mapping['date']]
                try:
                    # 尝试多种日期格式解析
                    date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y']
                    parsed_date = None
                    
                    if isinstance(date_str, datetime):
                        parsed_date = date_str.strftime('%Y-%m-%d')
                    else:
                        for fmt in date_formats:
                            try:
                                parsed_date = datetime.strptime(str(date_str), fmt).strftime('%Y-%m-%d')
                                break
                            except ValueError:
                                continue
                    
                    if not parsed_date:
                        errors.append(f"无法解析日期: {date_str}")
                        continue
                except Exception as e:
                    errors.append(f"日期解析错误: {date_str}, {str(e)}")
                    continue
                
                # 准备考勤数据
                attendance_data = {
                    'employee_id': employee['id'],
                    'date': parsed_date,
                    'custom_data': {}
                }
                
                # 处理标准字段
                standard_fields = ['status', 'work_hours', 'late_minutes', 'early_leave_minutes', 'overtime_hours', 'absence_days']
                for field in standard_fields:
                    if field in mapping and mapping[field] and mapping[field] in row:
                        attendance_data[field] = row[mapping[field]]
                
                # 处理自定义字段
                for key, value in mapping.items():
                    if key not in required_fields and key not in standard_fields and value and value in row:
                        attendance_data['custom_data'][key] = row[value]
                
                # 创建考勤记录
                Attendance.create(attendance_data)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"处理行数据时出错: {str(e)}")
        
        # 清理临时文件
        os.remove(temp_file_path)
        
        return {
            'imported_count': imported_count,
            'errors': errors
        }
    
    def get_attendance_data(self, month=None):
        """获取考勤数据
        
        Args:
            month: 月份，格式为YYYY-MM，如果为None则返回所有数据
            
        Returns:
            包含考勤数据列表和总数的字典
        """
        try:
            if month:
                # 获取指定月份的考勤数据
                result = Attendance.get_by_month(month)
                return {'items': result, 'total': len(result)}
            else:
                # 获取所有考勤数据可能会很多，这里可以考虑分页或限制返回最近的数据
                query = 'SELECT * FROM attendance ORDER BY date DESC LIMIT 1000'
                # 使用正确的导入路径
                from backend.database.db import execute_query
                result = execute_query(query)
                return {'items': result, 'total': len(result)}
        except Exception as e:
            # 记录错误并返回空结果，避免前端崩溃
            import logging
            logger = logging.getLogger('hrzhushou.attendance')
            logger.error(f"获取考勤数据失败: {str(e)}")
            return {'items': [], 'total': 0}
    
    def get_employee_attendance(self, employee_id, month):
        """获取指定员工在指定月份的考勤数据
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            
        Returns:
            考勤数据列表
        """
        return Attendance.get_by_employee_and_month(employee_id, month)
    
    def calculate_attendance_summary(self, employee_id, month):
        """计算员工在指定月份的考勤汇总数据
        
        Args:
            employee_id: 员工ID
            month: 月份，格式为YYYY-MM
            
        Returns:
            考勤汇总数据
        """
        attendance_records = self.get_employee_attendance(employee_id, month)
        
        # 初始化汇总数据
        summary = {
            'total_days': len(attendance_records),
            'normal_days': 0,
            'late_count': 0,
            'early_leave_count': 0,
            'absence_days': 0,
            'total_late_minutes': 0,
            'total_early_leave_minutes': 0,
            'total_overtime_hours': 0,
            'custom_summary': {}
        }
        
        # 汇总数据
        for record in attendance_records:
            if record['status'] == '正常':
                summary['normal_days'] += 1
            
            if record['late_minutes'] > 0:
                summary['late_count'] += 1
                summary['total_late_minutes'] += record['late_minutes']
            
            if record['early_leave_minutes'] > 0:
                summary['early_leave_count'] += 1
                summary['total_early_leave_minutes'] += record['early_leave_minutes']
            
            if record['absence_days'] > 0:
                summary['absence_days'] += record['absence_days']
            
            if record['overtime_hours'] > 0:
                summary['total_overtime_hours'] += record['overtime_hours']
            
            # 处理自定义数据
            custom_data = json.loads(record['custom_data']) if isinstance(record['custom_data'], str) else record['custom_data']
            for key, value in custom_data.items():
                if key not in summary['custom_summary']:
                    summary['custom_summary'][key] = 0
                
                try:
                    # 尝试将值转换为数字并累加
                    summary['custom_summary'][key] += float(value)
                except (ValueError, TypeError):
                    # 如果不是数字，则计数
                    summary['custom_summary'][key] += 1
        
        return summary