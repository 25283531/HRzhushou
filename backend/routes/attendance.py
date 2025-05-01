# 考勤相关路由

from flask import Blueprint, jsonify, request
from ..services.attendance import AttendanceService

# 创建蓝图
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/import', methods=['POST'])
def import_attendance():
    try:
        file = request.files['file']
        mapping = request.form.get('mapping', '{}')
        service = AttendanceService()
        result = service.import_attendance_data(file, mapping)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@attendance_bp.route('/list', methods=['GET'])
def list_attendance():
    try:
        month = request.args.get('month')
        service = AttendanceService()
        result = service.get_attendance_data(month)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400