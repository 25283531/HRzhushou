# 社保相关路由

from flask import Blueprint, jsonify, request
from ..services.social_security import SocialSecurityService

# 创建蓝图
social_security_bp = Blueprint('social_security', __name__)

@social_security_bp.route('/calculate', methods=['POST'])
def calculate_social_security():
    try:
        data = request.json
        service = SocialSecurityService()
        result = service.calculate_social_security(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@social_security_bp.route('/items', methods=['GET'])
def get_insurance_items():
    try:
        service = SocialSecurityService()
        result = service.get_insurance_items()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@social_security_bp.route('/groups', methods=['GET'])
def get_insurance_groups():
    try:
        service = SocialSecurityService()
        result = service.get_insurance_groups()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400