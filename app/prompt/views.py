from . import prompt
from .models import Prompt
from database import *

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request

# 查询用户的 prompts
@prompt.route('/user', methods=['GET'])
@jwt_required()
def get_prompts_by_user():
    user_id = get_jwt_identity()
    propmts = Prompt.query.filter_by(user_id=user_id).all()
    return jsonify({'prompts': [p.to_dict() for p in propmts], 'code': '200'})

# 更新用户的 prompts
@prompt.route('/update_prompts', methods=['PUT'])
@jwt_required()
def update_prompt():
    data = request.get_json()
    prompts = data
    if prompts is None:
        return jsonify({'message': '查询失败!', 'code': '400'})
    
    for p in prompts:
        prompt_id = p["id"]
        prompt = Prompt.query.get(prompt_id)
        prompt.content = p['content']

    db.session.commit()
    return jsonify({'message': '更新成功!', 'code': '200'})