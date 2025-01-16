from . import article_config
from .models import UserFile, ArticleConfig

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from sqlalchemy import select
from ..utils import model_to_dict

# 查询用户的所有整文配置
@article_config.route('/get_configs', methods=['GET'])
@jwt_required()
def get_configs():
  user_id = get_jwt_identity()
  configs = []
  stmt = select(ArticleConfig).where(ArticleConfig.user_id==user_id)
  
  try:
    for row in db.session.execute(stmt):
      article_config = row[0]
      configs.append(model_to_dict(article_config))
    return jsonify({'configs': configs, 'code': 200 })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '查询失败！', 'code': 500 })


# 增加一个新的配置
@article_config.route('/add_config', methods=['POST'])
@jwt_required()
def add_config():
  form = request.form
  user_id = get_jwt_identity()
  
  title = form['title']
  search_engine=form['search_engine']
  gpt = form['gpt']
  # convert 'true' to True
  networking_RAG = (form['networking_RAG'] == 'true')
  local_RAG_support = (form['local_RAG_support'] == 'true')
  step_by_step = (form['step_by_step'] == 'true')
  
  article_config = ArticleConfig(title=title, search_engine=search_engine, gpt=gpt, networking_RAG=networking_RAG, local_RAG=local_RAG_support, step_by_step=step_by_step, user_id=user_id)
  if local_RAG_support:
    files = request.files.items()
    for file_tuple in files:
      file = UserFile(file_name=file_tuple[0], file_data=file_tuple[1].read())
      article_config.local_RAG_files.append(file)
  
  try:
    db.session.add(article_config)
    db.session.commit()
    return jsonify({'message': '新增配置成功！', 'code': 200, 'id': article_config.id})
  except Exception as e:
      print(f"处理响应时发生错误: {e}")
      return jsonify({'message': '新增配置发生错误！', 'code': 500})


# 更新某个配置
@article_config.route('/update_config/<int:config_id>', methods=['PUT'])
@jwt_required()
def update_config(config_id):
  article_config = db.session.get(ArticleConfig, config_id)
  
  form = request.form
  article_config.title = form['title']
  article_config.search_engine=form['search_engine']
  article_config.gpt = form['gpt']
  # convert 'true' to True
  article_config.networking_RAG = (form['networking_RAG'] == 'true')
  article_config.local_RAG = (form['local_RAG_support'] == 'true')
  article_config.step_by_step = (form['step_by_step'] == 'true')
  
  if article_config.local_RAG:
    article_config.local_RAG_files = []
    files = request.files.items()
    for file_tuple in files:
      file = UserFile(file_name=file_tuple[0], file_data=file_tuple[1].read())
      article_config.local_RAG_files.append(file)

  try:
    db.session.commit()
    return jsonify({'message': '更新成功', 'code': 200})
  except Exception as e:
    print(e)
    return jsonify({'message': '更新失败', 'code': 500})

# 删除某个配置
@article_config.route('/delete_config/<int:config_id>', methods=['DELETE'])
@jwt_required()
def delete_config(config_id):
  try:
      article_config = db.session.get(ArticleConfig, config_id)
      db.session.delete(article_config)
      db.session.commit()
      return jsonify({'message': '删除成功！', 'code': 200 })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '删除失败！', 'code': 500 })