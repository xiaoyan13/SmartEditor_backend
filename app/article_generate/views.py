from . import article_generate
from .models import UserFile, ArticleConfig, ArticlePrompt

from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from sqlalchemy import select
from ..utils.model_to_dict import model_to_dict

from .task_manager import Task

# 查询用户的所有整文配置
@article_generate.route('/get_configs', methods=['GET'])
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
@article_generate.route('/add_config', methods=['POST'])
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
  
  # 每个配置都对应一个空 prompt
  article_config.article_prompt = ArticlePrompt(content="")
  try:
    db.session.add(article_config)
    db.session.commit()
    return jsonify({'message': '新增配置成功！', 'code': 200, 'id': article_config.id})
  except Exception as e:
      print(f"处理响应时发生错误: {e}")
      return jsonify({'message': '新增配置发生错误！', 'code': 500})


# 更新某个配置
@article_generate.route('/update_config/<int:config_id>', methods=['PUT'])
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
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '更新失败', 'code': 500})

# 删除某个配置
@article_generate.route('/delete_config/<int:config_id>', methods=['DELETE'])
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


# 修改某个 article_prompt
@article_generate.route('/change_prompt/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
  try:
    data = request.get_json()
    new_content = data["content"]
    article_prompt =  db.session.get(ArticlePrompt, prompt_id)
    article_prompt.content = new_content
    db.session.commit()
    return jsonify({'code': 200 })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '后端服务器暂不可用！', 'code': 500 })
  
# 新建任务并运行
@article_generate.route('/create_generate_task/<int:config_id>', methods=['POST'])
@jwt_required()
def create_generate_task(config_id):
  try:
    data = request.get_json()
    article_title = data["article_title"]
    new_task = Task(config_id, article_title)
    new_task.run()
    id = new_task.id
    return jsonify({'message': '成功', 'code': 200, 'task_id': id })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '创建任务失败！', 'code': 500 })

# 根据任务 ID 获取任务状态, 任务可能为空
@article_generate.route('/get_task_by_id/<string:task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
  try:
    task = Task.get_task_by_id(task_id)
    if task:
      task = task.to_dict()
    return jsonify({'message': '成功', 'code': 200, 'task': task })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '获取任务异常！', 'code': 500 })

# 获取某文章配置所关联的所有任务
@article_generate.route('/get_task_by_config/<int:config_id>', methods=['GET'])
@jwt_required()
def get_task_by_config_id(config_id):
  try:
      tasks = Task.get_tasks_by_config_id(config_id=config_id)
      return jsonify({'message': '成功', 'code': 200, 'tasks': [task.to_dict() for task in tasks] })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '获取任务异常！', 'code': 500 })


### 获取任务的结果，供心跳机制定时查询使用。 ---
# search_result
@article_generate.route('/task/<string:task_id>/search_result', methods=['GET'])
@jwt_required()
def get_search_result(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    search_result = task.search_result
    return jsonify({'code': 200, 'search_result': search_result })

# network_RAG_search_result
@article_generate.route('/task/<string:task_id>/network_RAG_search_result', methods=['GET'])
@jwt_required()
def get_network_RAG_search_result(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    network_RAG_search_result = task.network_RAG_search_result
    return jsonify({'code': 200, 'network_RAG_search_result': network_RAG_search_result })

# local_RAG_search_result
@article_generate.route('/task/<string:task_id>/local_RAG_search_result', methods=['GET'])
@jwt_required()
def get_local_RAG_search_result(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    local_RAG_search_result = task.local_RAG_search_result
    return jsonify({'code': 200, 'local_RAG_search_result': local_RAG_search_result })

# outline_result
@article_generate.route('/task/<string:task_id>/outline_result', methods=['GET'])
@jwt_required()
def get_outline_result(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    outline_result = task.outline_result
    return jsonify({'code': 200, 'outline_result': outline_result })

# generate_document
@article_generate.route('/task/<string:task_id>/generate_document', methods=['GET'])
@jwt_required()
def generate_document(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    document_generator = task.get_document_generator()
    return Response(document_generator, content_type='text/event-stream')

### ---


# 根据用户输入的大纲生成文档
@article_generate.route('/task/<string:task_id>/generate_doc_by_outline', methods=['POST'])
@jwt_required()
def generate_doc_by_outline(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    data = request.get_json()
    outline = data["outline"]
    task.outline_result = outline

    document_generator = task.get_document_generator()
    return Response(document_generator, content_type='text/event-stream')