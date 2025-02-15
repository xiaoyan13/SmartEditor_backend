from . import prompt
from .models import Prompt, Template, TemplateOption
from database import *

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request
from app.utils.model_to_dict import model_to_dict

# 查询用户的润色等 prompts
@prompt.route('/user', methods=['GET'])
@jwt_required()
def get_prompts_by_user():
    user_id = get_jwt_identity()
    prompts = Prompt.query.filter_by(user_id=user_id).all()
    return jsonify({'prompts': [p.to_dict() for p in prompts], 'code': '200'})

# 更新用户的润色等 prompts
@prompt.route('/update_prompts', methods=['PUT'])
@jwt_required()
def update_prompt():
    data = request.get_json()
    prompts = data
    if prompts is None:
        return jsonify({'message': '更新失败!', 'code': '400'})
    
    for p in prompts:
        prompt_id = p["id"]
        prompt = Prompt.query.get(prompt_id)
        prompt.content = p['content']

    db.session.commit()
    return jsonify({'message': '更新成功!', 'code': '200'})

# 查询用户的模板
@prompt.route('/user/templates', methods=['GET'])
@jwt_required()
def get_templates_by_user():
    user_id = get_jwt_identity()
    templates = Template.query.filter_by(user_id=user_id).all()
    templates =  [model_to_dict(t) for t in templates]
    return jsonify({'templates': templates, 'code': '200'})

# 更新用户的模板
@prompt.route('/update_templates', methods=['PUT'])
@jwt_required()
def update_templates():
    data = request.get_json()
    templates = data
    if templates is None:
        return jsonify({'message': '更新失败!', 'code': '400'})
    
    for t in templates:
        template_id = t["id"]
        template = Template.query.get(template_id)
        options = t["options"]
        new_options = [TemplateOption(title=option["title"], prompt=option["prompt"]) for option in options]
        template.options = new_options

    db.session.commit()
    return jsonify({'message': '更新成功!', 'code': '200'})