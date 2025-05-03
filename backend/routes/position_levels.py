from flask import Blueprint, request, jsonify
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.models.position_levels import (
    create_tables,
    get_all_level_types,
    create_level_type,
    update_level_type,
    delete_level_type,
    get_all_position_levels,
    get_position_levels_by_type,
    create_position_level,
    update_position_level,
    delete_position_level
)

# 创建蓝图
bp = Blueprint('position_levels', __name__)
logger.info("创建position_levels蓝图")

# 确保数据库表已创建
create_tables()
logger.info("职位职级表已创建")

# 职级类型路由
@bp.route('/types', methods=['GET'])
def list_level_types():
    """获取所有职级类型"""
    logger.info("收到GET /types请求")
    try:
        types = get_all_level_types()
        types_list = []
        for type_item in types:
            type_dict = dict(type_item)
            type_dict['is_active'] = bool(type_dict['is_active'])
            types_list.append(type_dict)
        
        logger.info(f"返回{len(types_list)}个职级类型")
        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': types_list
        })
    except Exception as e:
        logger.error(f"获取职级类型列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'获取职级类型列表失败：{str(e)}'
        }), 500

@bp.route('/types', methods=['POST'])
def add_level_type():
    """创建职级类型"""
    logger.info("收到POST /types请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        type_id = create_level_type(data)
        logger.info(f"创建职级类型成功，ID: {type_id}")
        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': {'id': type_id}
        })
    except Exception as e:
        logger.error(f"创建职级类型失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'创建职级类型失败：{str(e)}'
        }), 500

@bp.route('/types/<int:type_id>', methods=['PUT'])
def modify_level_type(type_id):
    """更新职级类型"""
    logger.info(f"收到PUT /types/{type_id}请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        success = update_level_type(type_id, data)
        if success:
            logger.info(f"更新职级类型成功，ID: {type_id}")
            return jsonify({
                'code': 0,
                'message': '更新成功'
            })
        logger.warning(f"职级类型不存在，ID: {type_id}")
        return jsonify({
            'code': 1,
            'message': '职级类型不存在'
        }), 404
    except Exception as e:
        logger.error(f"更新职级类型失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'更新职级类型失败：{str(e)}'
        }), 500

@bp.route('/types/<int:type_id>', methods=['DELETE'])
def remove_level_type(type_id):
    """删除职级类型"""
    logger.info(f"收到DELETE /types/{type_id}请求")
    try:
        success = delete_level_type(type_id)
        if success:
            logger.info(f"删除职级类型成功，ID: {type_id}")
            return jsonify({
                'code': 0,
                'message': '删除成功'
            })
        logger.warning(f"职级类型不存在，ID: {type_id}")
        return jsonify({
            'code': 1,
            'message': '职级类型不存在'
        }), 404
    except Exception as e:
        logger.error(f"删除职级类型失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'删除职级类型失败：{str(e)}'
        }), 500

# 职级路由
@bp.route('/levels', methods=['GET'])
def list_position_levels():
    """获取所有职级"""
    logger.info("收到GET /levels请求")
    try:
        type_id = request.args.get('type_id', type=int)
        if type_id:
            levels = get_position_levels_by_type(type_id)
        else:
            levels = get_all_position_levels()
        
        levels_list = []
        for level in levels:
            level_dict = dict(level)
            level_dict['is_active'] = bool(level_dict['is_active'])
            levels_list.append(level_dict)
        
        logger.info(f"返回{len(levels_list)}个职级")
        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': levels_list
        })
    except Exception as e:
        logger.error(f"获取职级列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'获取职级列表失败：{str(e)}'
        }), 500

@bp.route('/levels', methods=['POST'])
def add_position_level():
    """创建职级"""
    logger.info("收到POST /levels请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        level_id = create_position_level(data)
        logger.info(f"创建职级成功，ID: {level_id}")
        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': {'id': level_id}
        })
    except Exception as e:
        logger.error(f"创建职级失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'创建职级失败：{str(e)}'
        }), 500

@bp.route('/levels/<int:level_id>', methods=['PUT'])
def modify_position_level(level_id):
    """更新职级"""
    logger.info(f"收到PUT /levels/{level_id}请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        success = update_position_level(level_id, data)
        if success:
            logger.info(f"更新职级成功，ID: {level_id}")
            return jsonify({
                'code': 0,
                'message': '更新成功'
            })
        logger.warning(f"职级不存在，ID: {level_id}")
        return jsonify({
            'code': 1,
            'message': '职级不存在'
        }), 404
    except Exception as e:
        logger.error(f"更新职级失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'更新职级失败：{str(e)}'
        }), 500

@bp.route('/levels/<int:level_id>', methods=['DELETE'])
def remove_position_level(level_id):
    """删除职级"""
    logger.info(f"收到DELETE /levels/{level_id}请求")
    try:
        success = delete_position_level(level_id)
        if success:
            logger.info(f"删除职级成功，ID: {level_id}")
            return jsonify({
                'code': 0,
                'message': '删除成功'
            })
        logger.warning(f"职级不存在，ID: {level_id}")
        return jsonify({
            'code': 1,
            'message': '职级不存在'
        }), 404
    except Exception as e:
        logger.error(f"删除职级失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'删除职级失败：{str(e)}'
        }), 500 