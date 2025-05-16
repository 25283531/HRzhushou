from flask import Blueprint, request, jsonify
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.models.salary_items import (
    create_tables,
    get_all_salary_items,
    create_salary_item,
    update_salary_item,
    delete_salary_item,
    get_all_matching_rules,
    create_matching_rule,
    update_matching_rule,
    delete_matching_rule
)

# 创建蓝图
bp = Blueprint('salary_items', __name__)
logger.info("创建salary_items蓝图")

# 确保数据库表已创建
create_tables()
logger.info("数据库表已创建")

# 薪酬项路由
@bp.route('/salary-groups/<int:group_id>/items', methods=['GET'])
def list_salary_items(group_id):
    logger.info("收到GET /items请求")
    try:
        items = get_all_salary_items()
        # 将sqlite3.Row对象转换为字典
        items_list = []
        for item in items:
            item_dict = dict(item)
            item_dict['is_fixed'] = bool(item_dict['is_fixed'])
            items_list.append(item_dict)
        
        logger.info(f"返回{len(items_list)}个薪酬项")
        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': items_list
        })
    except Exception as e:
        logger.error(f"获取薪酬项列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'获取薪酬项列表失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/items', methods=['POST'])
def add_salary_item(group_id):
    logger.info("收到POST /items请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        item_id = create_salary_item(data)
        logger.info(f"创建薪酬项成功，ID: {item_id}")
        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': {'id': item_id}
        })
    except Exception as e:
        logger.error(f"创建薪酬项失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'创建薪酬项失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/items/<int:item_id>', methods=['PUT'])
def modify_salary_item(group_id, item_id):
    logger.info(f"收到PUT /items/{item_id}请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        success = update_salary_item(item_id, data)
        if success:
            logger.info(f"更新薪酬项成功，ID: {item_id}")
            return jsonify({
                'code': 0,
                'message': '更新成功'
            })
        logger.warning(f"薪酬项不存在，ID: {item_id}")
        return jsonify({
            'code': 1,
            'message': '薪酬项不存在'
        }), 404
    except Exception as e:
        logger.error(f"更新薪酬项失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'更新薪酬项失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/items/<int:item_id>', methods=['DELETE'])
def remove_salary_item(group_id, item_id):
    logger.info(f"收到DELETE /items/{item_id}请求")
    try:
        success = delete_salary_item(item_id)
        if success:
            logger.info(f"删除薪酬项成功，ID: {item_id}")
            return jsonify({
                'code': 0,
                'message': '删除成功'
            })
        logger.warning(f"薪酬项不存在，ID: {item_id}")
        return jsonify({
            'code': 1,
            'message': '薪酬项不存在'
        }), 404
    except Exception as e:
        logger.error(f"删除薪酬项失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'删除薪酬项失败：{str(e)}'
        }), 500

# 匹配规则路由
@bp.route('/salary-groups/<int:group_id>/matches', methods=['GET'])
def list_matching_rules(group_id):
    logger.info("收到GET /rules请求")
    try:
        rules = get_all_matching_rules()
        # 将sqlite3.Row对象转换为字典
        rules_list = []
        for rule in rules:
            rule_dict = dict(rule)
            rule_dict['is_active'] = bool(rule_dict['is_active'])
            if rule_dict['salary_items']:
                rule_dict['salary_items'] = [int(x) for x in rule_dict['salary_items'].split(',')]
            else:
                rule_dict['salary_items'] = []
            rules_list.append(rule_dict)
        
        logger.info(f"返回{len(rules_list)}个匹配规则")
        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': rules_list
        })
    except Exception as e:
        logger.error(f"获取匹配规则列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'获取匹配规则列表失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/matches', methods=['POST'])
def add_matching_rule(group_id):
    logger.info("收到POST /rules请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        rule_id = create_matching_rule(data)
        logger.info(f"创建匹配规则成功，ID: {rule_id}")
        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': {'id': rule_id}
        })
    except Exception as e:
        logger.error(f"创建匹配规则失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'创建匹配规则失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/matches/<int:rule_id>', methods=['PUT'])
def modify_matching_rule(group_id, rule_id):
    logger.info(f"收到PUT /rules/{rule_id}请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        success = update_matching_rule(rule_id, data)
        if success:
            logger.info(f"更新匹配规则成功，ID: {rule_id}")
            return jsonify({
                'code': 0,
                'message': '更新成功'
            })
        logger.warning(f"匹配规则不存在，ID: {rule_id}")
        return jsonify({
            'code': 1,
            'message': '匹配规则不存在'
        }), 404
    except Exception as e:
        logger.error(f"更新匹配规则失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'更新匹配规则失败：{str(e)}'
        }), 500

@bp.route('/salary-groups/<int:group_id>/matches/<int:rule_id>', methods=['DELETE'])
def remove_matching_rule(group_id, rule_id):
    logger.info(f"收到DELETE /rules/{rule_id}请求")
    try:
        success = delete_matching_rule(rule_id)
        if success:
            logger.info(f"删除匹配规则成功，ID: {rule_id}")
            return jsonify({
                'code': 0,
                'message': '删除成功'
            })
        logger.warning(f"匹配规则不存在，ID: {rule_id}")
        return jsonify({
            'code': 1,
            'message': '匹配规则不存在'
        }), 404
    except Exception as e:
        logger.error(f"删除匹配规则失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 1,
            'message': f'删除匹配规则失败：{str(e)}'
        }), 500