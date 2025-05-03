# 薪资相关路由

from flask import Blueprint, jsonify, request
from ..services.salary import SalaryService
from ..database.models import SalaryGroup  # 假设存在 SalaryGroup 模型

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

@salary_bp.route('/salary_groups', methods=['POST'])
def create_salary_group():
    """创建新的薪资组"""
    try:
        data = request.json
        service = SalaryService()
        result = service.create_salary_group(data)
        # 假设 service 返回的是包含新组信息的字典或ID
        return jsonify({'success': True, 'data': result}), 201 # 201 Created
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400 # Bad Request for validation errors
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({'success': False, 'error': '创建薪资组时发生内部错误'}), 500 # Internal Server Error

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