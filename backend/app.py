import os
import sys
from flask import Flask, jsonify, request
from database.db import init_db, get_db_connection
from services.attendance import AttendanceService
from services.employee import EmployeeService
from services.salary import SalaryService
from services.social_security import SocialSecurityService

app = Flask(__name__)

# 初始化数据库
@app.before_first_request
def setup():
    init_db()

# 考勤数据相关路由
@app.route('/api/attendance/import', methods=['POST'])
def import_attendance():
    try:
        file = request.files['file']
        mapping = request.form.get('mapping', '{}')
        service = AttendanceService()
        result = service.import_attendance_data(file, mapping)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/attendance/list', methods=['GET'])
def list_attendance():
    try:
        month = request.args.get('month')
        service = AttendanceService()
        result = service.get_attendance_data(month)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# 员工信息相关路由
@app.route('/api/employee/list', methods=['GET'])
def list_employees():
    try:
        service = EmployeeService()
        result = service.get_all_employees()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/employee/add', methods=['POST'])
def add_employee():
    try:
        data = request.json
        service = EmployeeService()
        result = service.add_employee(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/employee/update/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.json
        service = EmployeeService()
        result = service.update_employee(employee_id, data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/employee/position-change', methods=['POST'])
def add_position_change():
    try:
        data = request.json
        service = EmployeeService()
        result = service.add_position_change(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# 薪资计算相关路由
@app.route('/api/salary/calculate', methods=['POST'])
def calculate_salary():
    try:
        data = request.json
        service = SalaryService()
        result = service.calculate_salary(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/salary/history', methods=['GET'])
def get_salary_history():
    try:
        month = request.args.get('month')
        employee_id = request.args.get('employee_id')
        service = SalaryService()
        result = service.get_salary_history(month, employee_id)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# 社保相关路由
@app.route('/api/social-security/calculate', methods=['POST'])
def calculate_social_security():
    try:
        data = request.json
        service = SocialSecurityService()
        result = service.calculate_social_security(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)