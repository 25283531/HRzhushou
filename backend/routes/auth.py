from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..database.models import User
from ..database.db import execute_query, get_current_time

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    if User.get_by_username(username):
        return jsonify({'message': '用户名已存在'}), 409

    hashed_password = generate_password_hash(password)
    
    try:
        User.create({'username': username, 'password': hashed_password})
        return jsonify({'message': '用户注册成功'}), 201
    except Exception as e:
        # Log the exception e
        return jsonify({'message': '注册失败，请稍后再试'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = User.get_by_username(username)

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': '用户名或密码错误'}), 401

    access_token = create_access_token(identity=user['id'])
    return jsonify(access_token=access_token), 200

def init_auth_routes(app):
    app.register_blueprint(auth_bp)