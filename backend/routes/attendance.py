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
        import logging
        logger = logging.getLogger('hrzhushou.attendance_api')
        logger.info(f"考勤数据查询参数: month={month}")
        logger.info(f"考勤数据查询结果: {result}")
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        import logging
        logger = logging.getLogger('hrzhushou.attendance_api')
        logger.error(f"获取考勤数据失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400

@attendance_bp.route('/rules', methods=['POST'])
def save_attendance_rules():
    try:
        data = request.get_json()
        # 这里假设直接保存到本地文件或数据库，示例为保存到本地 JSON 文件
        import json, os
        rules = data.get('rules') if isinstance(data, dict) else data
        if not isinstance(rules, list):
            # 兼容前端传递对象的情况，转为数组
            rules = [rules] if rules else []
        save_path = os.path.join(os.path.dirname(__file__), '../data/attendance_rules.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True, 'data': rules})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400