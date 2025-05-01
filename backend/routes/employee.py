# 员工相关路由

from flask import Blueprint, jsonify, request
from ..services.employee import EmployeeService

# 创建蓝图
employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/list', methods=['GET'])
def list_employees():
    try:
        service = EmployeeService()
        result = service.get_all_employees()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@employee_bp.route('/add', methods=['POST'])
def add_employee():
    try:
        data = request.json
        service = EmployeeService()
        result = service.add_employee(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@employee_bp.route('/update/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.json
        service = EmployeeService()
        result = service.update_employee(employee_id, data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@employee_bp.route('/position-change', methods=['POST'])
def add_position_change():
    try:
        data = request.json
        service = EmployeeService()
        result = service.add_position_change(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400