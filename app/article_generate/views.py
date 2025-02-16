from . import article_generate
from .models import UserFile, ArticleConfig, ArticlePrompt, SystemPrompt, Step

from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from sqlalchemy import select
from ..utils.model_to_dict import model_to_dict
import json

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
  step_by_step = int(form['step_by_step'])
  # convert 'true' to True
  networking_RAG = (form['networking_RAG'] == 'true')
  local_RAG_support = (form['local_RAG_support'] == 'true')
  
  article_config = ArticleConfig(title=title, search_engine=search_engine, gpt=gpt, networking_RAG=networking_RAG, local_RAG=local_RAG_support, step_by_step=step_by_step, user_id=user_id)
  
  system_prompt = form['system_prompt']
  article_config.system_prompt = SystemPrompt(content=system_prompt)
  
  # extract steps' info
  steps = json.loads(form['steps'])
  steps = [Step(title=step["title"], prompt=step["prompt"], step_order=step["step_order"]) for step in steps]
  article_config.steps = steps
  
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
  article_config.step_by_step = int(form['step_by_step'])
  article_config.system_prompt = SystemPrompt(content=form['system_prompt'])
  
  # convert 'true' to True
  article_config.networking_RAG = (form['networking_RAG'] == 'true')
  article_config.local_RAG = (form['local_RAG_support'] == 'true')
  
  # extract steps' info
  steps = json.loads(form['steps'])
  steps = [Step(prompt=step["prompt"], step_order=step["step_order"]) for step in steps]
  article_config.steps = steps
  
  if article_config.local_RAG:
    article_config.local_RAG_files = []
    files = request.files.items()
    for file_tuple in files:
      file = UserFile(file_name=file_tuple[0], file_data=file_tuple[1].read())
      article_config.local_RAG_files.append(file)

  try:
    db.session.commit()
    Task.clear_task_by_config_id(article_config.id) # clear all tasks related to it.
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
    title = data["title"]
    new_content = data["content"]
    article_prompt =  db.session.get(ArticlePrompt, prompt_id)
    article_prompt.content = new_content
    article_prompt.title = title
    db.session.commit()
    return jsonify({'code': 200 })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '后端服务器暂不可用！', 'code': 500 })


# 新建任务并运行
@article_generate.route('/create_generate_task/<int:config_id>/<int:step_n>', methods=['POST'])
@jwt_required()
def create_generate_task(config_id, step_n):
  try:
    data: dict = request.get_json()
    article_title = data.get("article_title")
    search_needed = data.get("search_needed")
    user_input = data.get("user_input")
    network_RAG_search_needed = data.get("network_RAG_search_needed")
    local_RAG_search_needed = data.get("local_RAG_search_needed")
    search_engine_used = data.get("search_engine")
    model_used = data.get("model_used")
    
    new_task = Task(config_id, 
                    step_n, 
                    article_title=article_title,
                    user_input=user_input,
                    search_needed=search_needed,
                    network_RAG_search_needed=network_RAG_search_needed,
                    local_RAG_search_needed=local_RAG_search_needed,
                    search_engine_used=search_engine_used,
                    model_used=model_used,
                )
    
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


### 获取任务的结果，供心跳机制定时查询使用。
# result_name: search_result | network_RAG_search_result | local_RAG_search_result
@article_generate.route('/task/<string:task_id>/<string:result_name>', methods=['GET'])
@jwt_required()
def get_search_result(task_id, result_name):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    if (result_name == 'search_result'):
      return jsonify({'code': 200, 'search_result': task.search_result })
    elif (result_name == 'network_RAG_search_result'):
      # network_RAG_search_result is a tuple
      return jsonify({'code': 200, 'network_RAG_search_result': task.network_RAG_search_result[0] })
    elif (result_name == 'local_RAG_search_result'):
      return jsonify({'code': 200, 'local_RAG_search_result': task.local_RAG_search_result })

# 获取任务目前生成的结果
@article_generate.route('/task/<string:task_id>', methods=['GET'])
@jwt_required()
def fetch_task_result(task_id):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    task_result = task.task_result
    generate_status = task.generate_status
    return jsonify({'code': 200, 'task_result': task_result, 'generate_status': generate_status})

# 获取任务的结果生成器
# task_type: comprehend_task | geneate_outline | generate_document | expand_document
@article_generate.route('/task/result_gen/<string:task_id>/<string:task_type>', methods=['GET'])
@jwt_required()
def fetch_task_result_generator(task_id, task_type):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    def start_generate_by_type(task_type, regenerate=False):
      if task_type == 'comprehend_task':
        task.start_comprehend_task(regenerate=regenerate)
      elif task_type == 'geneate_outline':
        task.start_geneate_outline(regenerate=regenerate)
      elif task_type == 'generate_document':
        task.start_generate_document(regenerate=regenerate)
      elif task_type == 'expand_document':
        task.start_expand_doc(regenerate=regenerate)
    
    def get_generator_by_type(task_type):
      if task_type == 'comprehend_task':
        return task.comprehend_task_generator
      elif task_type == 'geneate_outline':
        return task.outline_generator
      elif task_type == 'generate_document': 
        return task.doc_generator
      elif task_type == 'expand_document':
        return task.expand_doc_generator

    start_generate_by_type(task_type)
    generator = get_generator_by_type(task_type)
    return Response(generator, content_type='text/event-stream')

# 任务的重新生成
# task_type: comprehend_task | geneate_outline | generate_document | expand_document
@article_generate.route('/task/result_gen/<string:task_id>/<string:task_type>/regenerate', methods=['GET'])
@jwt_required()
def fetch_task_result_regenerator(task_id, task_type):
  task = Task.get_task_by_id(task_id)
  if (task is None):
    return jsonify({'message': '任务不存在！', 'code': 400 }) 
  else:
    def start_generate_by_type(task_type, regenerate=False):
      if task_type == 'comprehend_task':
        task.start_comprehend_task(regenerate=regenerate)
      elif task_type == 'geneate_outline':
        task.start_geneate_outline(regenerate=regenerate)
      elif task_type == 'generate_document':
        task.start_generate_document(regenerate=regenerate)
      elif task_type == 'expand_document':
        task.start_expand_doc(regenerate=regenerate)
    
    def get_generator_by_type(task_type):
      if task_type == 'comprehend_task':
        return task.comprehend_task_generator
      elif task_type == 'geneate_outline':
        return task.outline_generator
      elif task_type == 'generate_document': 
        return task.doc_generator
      elif task_type == 'expand_document':
        return task.expand_doc_generator

    start_generate_by_type(task_type, regenerate=True)
    generator = get_generator_by_type(task_type)
    return Response(generator, content_type='text/event-stream')

# 删除 config 关联的所有任务
@article_generate.route('/del_all_tasks/<int:config_id>', methods=['DELETE'])
@jwt_required()
def del_all_tasks(config_id):
  try:
    Task.clear_task_by_config_id(config_id=config_id)
    return jsonify({'code': 200 })
  except Exception as e:
    print(f"处理响应时发生错误: {e}")
    return jsonify({'message': '删除任务时异常！', 'code': 500 })