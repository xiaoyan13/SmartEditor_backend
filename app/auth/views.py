import os
import random
import json

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message

from database import *
from mail import mail
from . import auth
from .models import Users
from ..prompt.models import Prompt, Template, TemplateOption

#  生成验证码并发送邮件
@auth.route('/varify/<string:username>&<string:email>')
def varify(username, email):
    # 生成一个6位数的验证码
    verification_code = str(random.randint(100000, 999999))
    # 将验证码和用户的邮箱一起存储到 Redis 中
    redis_client.setex(f'verification_code:{email}', 300, verification_code)
    # 创建邮件消息
    msg = Message('【iflower】用户注册邮箱验证', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = ('Hi，【{}】：\n\n您正尝试通过本邮箱接收注册【iflower】时所需的验证码。\n\n'
                '验证码：【{}】，5分钟内有效，如非本人操作，请忽略本邮件。').format(username, verification_code)
    # 发送邮件
    mail.send(msg)
    return jsonify({'message': '验证码已发送，请注意查收！', 'code': 200})


# 用户注册
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # 从 Redis 中获取验证码
    verification_code = redis_client.get(f'verification_code:{data["email"]}')
    # 验证验证码
    if verification_code is None or data['verification_code'] != verification_code:
        return jsonify({'message': '验证码错误或已失效！', 'code': 400})
    # 验证邮箱是否已被注册
    if Users.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已被注册！', 'code': 400})
    # 注册新用户
    new_user = Users(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.flush()
    new_user_id = new_user.id
    # 创建用户的润色、优化等的默认 prompts
    default_prompt_path = os.path.join(os.getcwd(), 'app/prompt/default_prompt.json')
    with open(default_prompt_path, 'r') as file:
        default_prompt = json.load(file)
        for prompt in default_prompt:
            new_prompt = Prompt(title=prompt["title"], content=prompt["content"], user_id=new_user_id)
            db.session.add(new_prompt)
    # 创建用户的一些默认生成模板
    default_template_path = os.path.join(os.getcwd(), 'app/prompt/default_template.json')
    with open(default_template_path, 'r') as file:
        default_template = json.load(file)
        for template in default_template:
            options = [TemplateOption(title=option["title"], prompt=option["prompt"]) for option in template["options"]]
            new_template = Template(label=template["label"], icon=template["icon"], user_id=new_user_id, options=options)
            db.session.add(new_template)
    
    db.session.commit()
    return jsonify({'message': '用户注册成功！', 'code': 200})


# 用户登录
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # 验证用户是否存在
    user = Users.query.filter_by(email=data['email']).first()
    if user is None:
        return jsonify({'message': '邮箱未注册！', 'code': 400})
    # 验证密码是否正确
    if not user.check_password(data['password']):
        return jsonify({'message': '密码错误！', 'code': 400})
    # 用户登录成功，生成 JWT
    access_token = create_access_token(identity=user.id)
    # 将 JWT 发送给前端
    return jsonify({'message': '用户登录成功！', 'code': 200,
                    'data': {'access_token': access_token, 'username': user.username, 'email': user.email}})


# 重置密码验证
@auth.route("/reset_varify", methods=["GET"])
@jwt_required()
def reset_varify():
    # 使用get_jwt_identity访问当前用户的身份
    current_user = get_jwt_identity()
    user = Users.query.get(current_user)
    email = user.email
    # 生成一个6位数的验证码
    verification_code = str(random.randint(100000, 999999))
    # 将验证码和用户的邮箱一起存储到 Redis 中
    redis_client.setex(f'verification_code:{email}', 300, verification_code)
    # 创建邮件消息
    msg = Message('【iflower】用户密码重置', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = ('Hi，【{}】：\n\n您正尝试通过本邮箱重置【iflower】时所需的验证码。\n\n'
                '验证码：【{}】，5分钟内有效，如非本人操作，请忽略本邮件。').format(user.username, verification_code)
    # 发送邮件
    mail.send(msg)
    return jsonify({'message': '验证码已发送，请注意查收！', 'code': 200})


# 用户密码重置
@auth.route("/reset_password", methods=["POST"])
@jwt_required()
def reset_password():
    current_user = get_jwt_identity()
    user = Users.query.get(current_user)
    email = user.email
    data = request.get_json()
    # 从 Redis 中获取验证码
    verification_code = redis_client.get(f'verification_code:{email}')
    # 验证验证码
    if verification_code is None or data['verification_code'] != verification_code:
        return jsonify({'message': '验证码错误或已失效！', 'code': 400})
    # 重置用户密码
    user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': '用户密码重置成功！', 'code': 200})
