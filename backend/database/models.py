from datetime import datetime
import json
from .db import execute_query, get_current_time

class BaseModel:
    """基础模型类，提供通用的CRUD操作"""
    
    @classmethod
    def create(cls, data):
        """创建记录"""
        raise NotImplementedError("子类必须实现create方法")
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        raise NotImplementedError("子类必须实现get_by_id方法")
    
    @classmethod
    def update(cls, id, data):
        """更新记录"""
        raise NotImplementedError("子类必须实现update方法")
    
    @classmethod
    def delete(cls, id):
        """删除记录"""
        raise NotImplementedError("子类必须实现delete方法")

class Employee(BaseModel):
    """员工模型"""
    @classmethod
    def create_table(cls):
        query = '''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT,
            employee_number TEXT UNIQUE,
            id_card TEXT,
            department TEXT,
            position TEXT,
            entry_date DATE,
            leave_date DATE,
            custom_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        execute_query(query)

    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO employees (name, employee_id, id_card, department, position, 
                              entry_date, leave_date, custom_fields, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        custom_fields = json.dumps(data.get('custom_fields', {}))
        current_time = get_current_time()
        
        params = (
            data.get('name'),
            data.get('employee_id'),
            data.get('id_card'),
            data.get('department'),
            data.get('position'),
            data.get('entry_date'),
            data.get('leave_date'),
            custom_fields,
            current_time,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM employees WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM employees ORDER BY name'
        return execute_query(query)
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE employees SET 
            name = ?,
            employee_id = ?,
            id_card = ?,
            department = ?,
            position = ?,
            entry_date = ?,
            leave_date = ?,
            custom_fields = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        current_employee = cls.get_by_id(id)
        if not current_employee:
            return None
        
        custom_fields = json.dumps(data.get('custom_fields', {}))
        current_time = get_current_time()
        
        params = (
            data.get('name', current_employee['name']),
            data.get('employee_id', current_employee['employee_id']),
            data.get('id_card', current_employee['id_card']),
            data.get('department', current_employee['department']),
            data.get('position', current_employee['position']),
            data.get('entry_date', current_employee['entry_date']),
            data.get('leave_date', current_employee['leave_date']),
            custom_fields,
            current_time,
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM employees WHERE id = ?'
        return execute_query(query, (id,))

class User(BaseModel):
    """用户模型"""
    @classmethod
    def create_table(cls):
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        execute_query(query)

    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO users (username, password, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        '''
        # In a real application, hash the password before storing
        # from werkzeug.security import generate_password_hash
        # hashed_password = generate_password_hash(data.get('password'))
        current_time = get_current_time()
        params = (
            data.get('username'),
            data.get('password'), # Store hashed password in production
            current_time,
            current_time
        )
        return execute_query(query, params)

    @classmethod
    def get_by_username(cls, username):
        query = 'SELECT * FROM users WHERE username = ?'
        return execute_query(query, (username,), one=True)

    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM users WHERE id = ?'
        return execute_query(query, (id,), one=True)

    # update and delete methods can be added as needed

class PositionChange(BaseModel):
    """职位变动记录模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO position_changes 
            (employee_id, old_position, new_position, old_salary, new_salary, effective_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        current_time = get_current_time()
        
        params = (
            data.get('employee_id'),
            data.get('old_position'),
            data.get('new_position'),
            data.get('old_salary'),
            data.get('new_salary'),
            data.get('effective_date'),
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM position_changes WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_by_employee(cls, employee_id):
        query = 'SELECT * FROM position_changes WHERE employee_id = ? ORDER BY effective_date DESC'
        return execute_query(query, (employee_id,))
    
    @classmethod
    def get_by_month(cls, month):
        # 获取指定月份内的职位变动记录
        start_date = f"{month}-01"
        if month.endswith('12'):
            end_date = f"{int(month.split('-')[0])+1}-01-01"
        else:
            end_date = f"{month.split('-')[0]}-{int(month.split('-')[1])+1:02d}-01"
        
        query = '''
        SELECT * FROM position_changes 
        WHERE effective_date >= ? AND effective_date < ? 
        ORDER BY employee_id, effective_date
        '''
        
        return execute_query(query, (start_date, end_date))
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE position_changes SET 
            employee_id = ?,
            old_position = ?,
            new_position = ?,
            old_salary = ?,
            new_salary = ?,
            effective_date = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        
        params = (
            data.get('employee_id', current_record['employee_id']),
            data.get('old_position', current_record['old_position']),
            data.get('new_position', current_record['new_position']),
            data.get('old_salary', current_record['old_salary']),
            data.get('new_salary', current_record['new_salary']),
            data.get('effective_date', current_record['effective_date']),
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM position_changes WHERE id = ?'
        return execute_query(query, (id,))

class Attendance(BaseModel):
    """考勤数据模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO attendance 
            (employee_id, name, employee_number, id_card, month, should_attend_days, actual_attend_days, late_count, serious_late_count, early_leave_count, serious_early_leave_count, absenteeism_count, sick_leave_days, personal_leave_days, work_injury_leave_days, annual_leave_days, overtime_hours, date, status, work_hours, late_minutes, early_leave_minutes, absence_days, custom_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        custom_data = json.dumps(data.get('custom_data', {}))
        current_time = get_current_time()
        
        params = (
            data.get('employee_id'),
            data.get('name'),
            data.get('employee_number'),
            data.get('id_card'),
            data.get('month'),
            data.get('should_attend_days', 0),
            data.get('actual_attend_days', 0),
            data.get('late_count', 0),
            data.get('serious_late_count', 0),
            data.get('early_leave_count', 0),
            data.get('serious_early_leave_count', 0),
            data.get('absenteeism_count', 0),
            data.get('sick_leave_days', 0),
            data.get('personal_leave_days', 0),
            data.get('work_injury_leave_days', 0),
            data.get('annual_leave_days', 0),
            data.get('overtime_hours', 0),
            data.get('date'),
            data.get('status'),
            data.get('work_hours', 0),
            data.get('late_minutes', 0),
            data.get('early_leave_minutes', 0),
            data.get('absence_days', 0),
            custom_data,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM attendance WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_by_employee_and_month(cls, employee_id, month):
        # 获取指定员工在指定月份的考勤记录
        query = 'SELECT * FROM attendance WHERE employee_id = ? AND date LIKE ? ORDER BY date'
        return execute_query(query, (employee_id, f"{month}%"))
    
    @classmethod
    def get_by_month(cls, month):
        """获取指定月份的考勤数据
        
        Args:
            month: 月份，格式为YYYY-MM
            
        Returns:
            考勤数据列表
        """
        query = f"SELECT * FROM attendance WHERE date LIKE '{month}%' ORDER BY date DESC"
        from backend.database.db import execute_query
        return execute_query(query)
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE attendance SET 
            employee_id = ?,
            name = ?,
            employee_number = ?,
            id_card = ?,
            month = ?,
            should_attend_days = ?,
            actual_attend_days = ?,
            late_count = ?,
            serious_late_count = ?,
            early_leave_count = ?,
            serious_early_leave_count = ?,
            absenteeism_count = ?,
            sick_leave_days = ?,
            personal_leave_days = ?,
            work_injury_leave_days = ?,
            annual_leave_days = ?,
            overtime_hours = ?,
            date = ?,
            status = ?,
            work_hours = ?,
            late_minutes = ?,
            early_leave_minutes = ?,
            absence_days = ?,
            custom_data = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        custom_data = json.dumps(data.get('custom_data', current_record.get('custom_data', {})))
        params = (
            data.get('employee_id', current_record['employee_id']),
            data.get('name', current_record['name']),
            data.get('employee_number', current_record['employee_number']),
            data.get('id_card', current_record['id_card']),
            data.get('month', current_record['month']),
            data.get('should_attend_days', current_record['should_attend_days']),
            data.get('actual_attend_days', current_record['actual_attend_days']),
            data.get('late_count', current_record['late_count']),
            data.get('serious_late_count', current_record['serious_late_count']),
            data.get('early_leave_count', current_record['early_leave_count']),
            data.get('serious_early_leave_count', current_record['serious_early_leave_count']),
            data.get('absenteeism_count', current_record['absenteeism_count']),
            data.get('sick_leave_days', current_record['sick_leave_days']),
            data.get('personal_leave_days', current_record['personal_leave_days']),
            data.get('work_injury_leave_days', current_record['work_injury_leave_days']),
            data.get('annual_leave_days', current_record['annual_leave_days']),
            data.get('overtime_hours', current_record['overtime_hours']),
            data.get('date', current_record['date']),
            data.get('status', current_record['status']),
            data.get('work_hours', current_record['work_hours']),
            data.get('late_minutes', current_record['late_minutes']),
            data.get('early_leave_minutes', current_record['early_leave_minutes']),
            data.get('absence_days', current_record['absence_days']),
            custom_data,
            id
        )
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM attendance WHERE id = ?'
        return execute_query(query, (id,))

class SalaryGroup(BaseModel):
    """薪资组模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO salary_groups (name, description, formula, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        
        current_time = get_current_time()
        
        params = (
            data.get('name'),
            data.get('description'),
            data.get('formula'),
            current_time,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM salary_groups WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM salary_groups ORDER BY name'
        return execute_query(query)
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE salary_groups SET 
            name = ?,
            description = ?,
            formula = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        
        current_time = get_current_time()
        
        params = (
            data.get('name', current_record['name']),
            data.get('description', current_record['description']),
            data.get('formula', current_record['formula']),
            current_time,
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM salary_groups WHERE id = ?'
        return execute_query(query, (id,))

class SalaryRecord(BaseModel):
    """薪资记录模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO salary_records 
            (employee_id, month, base_salary, actual_salary, deductions, 
             insurance, tax, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        details = json.dumps(data.get('details', {}))
        current_time = get_current_time()
        
        params = (
            data.get('employee_id'),
            data.get('month'),
            data.get('base_salary', 0),
            data.get('actual_salary', 0),
            data.get('deductions', 0),
            data.get('insurance', 0),
            data.get('tax', 0),
            details,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM salary_records WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_by_employee_and_month(cls, employee_id, month):
        query = 'SELECT * FROM salary_records WHERE employee_id = ? AND month = ?'
        return execute_query(query, (employee_id, month), one=True)
    
    @classmethod
    def get_by_month(cls, month):
        query = 'SELECT * FROM salary_records WHERE month = ? ORDER BY employee_id'
        return execute_query(query, (month,))
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE salary_records SET 
            employee_id = ?,
            month = ?,
            base_salary = ?,
            actual_salary = ?,
            deductions = ?,
            insurance = ?,
            tax = ?,
            details = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        
        details = json.dumps(data.get('details', {}))
        
        params = (
            data.get('employee_id', current_record['employee_id']),
            data.get('month', current_record['month']),
            data.get('base_salary', current_record['base_salary']),
            data.get('actual_salary', current_record['actual_salary']),
            data.get('deductions', current_record['deductions']),
            data.get('insurance', current_record['insurance']),
            data.get('tax', current_record['tax']),
            details,
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM salary_records WHERE id = ?'
        return execute_query(query, (id,))

class SalaryItem(BaseModel):
    """薪酬项模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO salary_items 
            (name, code, type, description, calculation_formula, 
             is_fixed, default_value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        current_time = get_current_time()
        
        params = (
            data.get('name'),
            data.get('code'),
            data.get('type'),
            data.get('description'),
            data.get('calculation_formula'),
            data.get('is_fixed', True),
            data.get('default_value', 0),
            current_time,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM salary_items WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM salary_items ORDER BY code'
        return execute_query(query)
    
    @classmethod
    def get_by_code(cls, code):
        query = 'SELECT * FROM salary_items WHERE code = ?'
        return execute_query(query, (code,), one=True)
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE salary_items SET 
            name = ?,
            code = ?,
            type = ?,
            description = ?,
            calculation_formula = ?,
            is_fixed = ?,
            default_value = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        
        current_time = get_current_time()
        
        params = (
            data.get('name', current_record['name']),
            data.get('code', current_record['code']),
            data.get('type', current_record['type']),
            data.get('description', current_record['description']),
            data.get('calculation_formula', current_record['calculation_formula']),
            data.get('is_fixed', current_record['is_fixed']),
            data.get('default_value', current_record['default_value']),
            current_time,
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM salary_items WHERE id = ?'
        return execute_query(query, (id,))

class MatchingRule(BaseModel):
    """匹配规则模型"""
    
    @classmethod
    def create(cls, data):
        query = '''
        INSERT INTO matching_rules 
            (name, description, conditions, salary_items, priority,
             is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        conditions = json.dumps(data.get('conditions', {}))
        salary_items = json.dumps(data.get('salary_items', []))
        current_time = get_current_time()
        
        params = (
            data.get('name'),
            data.get('description'),
            conditions,
            salary_items,
            data.get('priority', 0),
            data.get('is_active', True),
            current_time,
            current_time
        )
        
        return execute_query(query, params)
    
    @classmethod
    def get_by_id(cls, id):
        query = 'SELECT * FROM matching_rules WHERE id = ?'
        return execute_query(query, (id,), one=True)
    
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM matching_rules ORDER BY priority DESC'
        return execute_query(query)
    
    @classmethod
    def get_active_rules(cls):
        query = 'SELECT * FROM matching_rules WHERE is_active = 1 ORDER BY priority DESC'
        return execute_query(query)
    
    @classmethod
    def update(cls, id, data):
        query = '''
        UPDATE matching_rules SET 
            name = ?,
            description = ?,
            conditions = ?,
            salary_items = ?,
            priority = ?,
            is_active = ?,
            updated_at = ?
        WHERE id = ?
        '''
        
        current_record = cls.get_by_id(id)
        if not current_record:
            return None
        
        conditions = json.dumps(data.get('conditions', {}))
        salary_items = json.dumps(data.get('salary_items', []))
        current_time = get_current_time()
        
        params = (
            data.get('name', current_record['name']),
            data.get('description', current_record['description']),
            conditions,
            salary_items,
            data.get('priority', current_record['priority']),
            data.get('is_active', current_record['is_active']),
            current_time,
            id
        )
        
        execute_query(query, params)
        return cls.get_by_id(id)
    
    @classmethod
    def delete(cls, id):
        query = 'DELETE FROM matching_rules WHERE id = ?'
        return execute_query(query, (id,))