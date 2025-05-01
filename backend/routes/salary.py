# 薪资相关路由

from flask import Blueprint, jsonify, request
from ..services.salary import SalaryService

# 创建蓝图
salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/calculate', methods=['POST'])
def calculate_salary():
    try:
        data = request.json
        service = SalaryService()
        result = service.calculate_salary(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@salary_bp.route('/history', methods=['GET'])
def get_salary_history():
    try:
        month = request.args.get('month')
        employee_id = request.args.get('employee_id')
        service = SalaryService()
        result = service.get_salary_history(month, employee_id)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400