import uuid
import threading
import time
from typing import Optional, Generator, Literal

from database import db
from .models import ArticleConfig, UserFile

from ..utils.model_to_dict import model_to_dict
from ..utils.tavily_search import do_tavily_ai_search
from ..utils.deal_prompt import extract_search_keywords
from ..utils.RAG_search import do_local_RAG_search_by_files
from ..utils.internet_search.google_search import do_google_serp_search
from ..utils.article_generation.outline_generate import outline_generate
from ..utils.article_generation.article_generate import article_generate
from ..utils.article_generation.article_expension import expand_doc_generate
from ..utils.task_comprehend import task_comprehend_generate

from sqlalchemy import select

# task id maps to task.
id_map: dict[str, "Task"] = {}

class Task:
  """
  Manager for article generation task.
  """
  
  @staticmethod
  def clear_task_by_config_id(config_id):
    """
    Clear all tasks which related to config_id in the map.
    If tasks that never be used always in the id_map, memory lackage caused.
    This is recently designed to be called in:
    `update_config()` in views.py, where a config updated its tasks will be refreshed(that is, delete them directly.)
    """
    keys = []
    for key in id_map:
      if (id_map[key].config_id == config_id):
        keys.append(key)
    for key in keys:
      del id_map[key]
  @staticmethod
  def get_tasks_by_config_id(config_id):
    result: list[Task] = []
    for task_id in id_map:
      task = id_map[task_id]
      if task.config_id == config_id:
        result.append(task)
    return result
  
  @staticmethod
  def get_task_by_id(id) -> "Task":
    return id_map.get(id)
  
  def __init__(self, 
      config_id: int,
      step_n: int,
      user_input: str = '', 
      search_needed=True,
      network_RAG_search_needed=True,
      model_used='',
      search_engine_used='',
      local_RAG_search_needed=True,
      article_title=None
  ):
    self.id = str(uuid.uuid4())
    self.config_id = config_id
    self.step_n = step_n
    
    if user_input:
      self.user_input = user_input
    if article_title:
      self.aritle_title = article_title
    
    config = db.session.get(ArticleConfig, self.config_id)
    def set_value(config_value, custom_value):
      return custom_value if custom_value is not None else config_value
    self.search_needed = search_needed
    self.network_RAG_search_needed = set_value(config.networking_RAG, network_RAG_search_needed)
    self.local_RAG_search_needed = set_value(config.local_RAG, local_RAG_search_needed)
    self.model_used = set_value(config.gpt, model_used)
    self.search_engine_used = set_value(config.search_engine, search_engine_used)

    id_map[self.id] = self
  
  id: str
  config_id: int # Every task has its corresponding article-gen config
  step_n: int = 0 # which step
  generate_status: Literal['undo', 'doing', 'done'] = "undo"
  user_input: str = ''
  task_result: str = ''
  # these are setted by users and override the config's corresponding value
  search_needed: bool = True
  network_RAG_search_needed: bool = True
  local_RAG_search_needed: bool = True
  model_used: str = ''
  search_engine_used: str = ''
  # these signs indicating current task working status
  search_ready: bool = False
  network_RAG_search_ready: bool = False
  local_RAG_search_ready: bool = False
  search_ended: bool = False # all search results is ready
  # the search results
  search_result = None
  network_RAG_search_result = None
  local_RAG_search_result = None
  # the target result geneartor, which represents this task's type
  comprehend_task_generator : Optional[Generator | None] = None
  outline_generator : Optional[Generator | None] = None
  doc_generator : Optional[Generator | None] = None
  expand_doc_generator : Optional[Generator | None] = None
  
  def run(self):
    """
    Run an task. Every task has a target(generating an outline, summary, expend article, and so on.).
    A task generates the target step by step sequentially:
    1. search the internet
    2. search the network RAG if setted
    3. search the local RAG if setted
    4. generate the target based on these results.
    These search are all selectable.
    
    Once result generated successfully, 
    `_clear()` is called automatically, so that task is expunged from the tasks queue.
    """
    
    # 这里选择使用线程来运行文章生成任务
    # Flask 并不希望用户创建线程: https://flask.palletsprojects.com/en/stable/design/#thread-locals
    # 使用线程会导致 Flask 上下文丢失。解决方案: 把任务需要的信息拿到, 传给线程。
    config = db.session.get(ArticleConfig, self.config_id)
    local_files = []
    if config.local_RAG:
      stmt = select(UserFile).where(UserFile.config_id==self.config_id)
      files_results = db.session.execute(stmt)
      for row in files_results:
        file = {
          "file_name": row[0].file_name,
          "file_data": row[0].file_data,
          "config_id": row[0].config_id,
        }
        local_files.append(file)
      
    config = model_to_dict(config)
    
    args = [config, ]
    if (local_files):
      args.append(local_files)
      
    try:
      thread = threading.Thread(target=self._run, args=args)
      thread.start()
    except Exception as e:
      print(f"任务 {self.id} 运行期间发生错误: {e}")

  def get_status(self, status_wanted) -> bool:
    return getattr(self, status_wanted)
  
  def start_comprehend_task(self, *args):
    comprehend_generator = task_comprehend_generate(*args)
    self.comprehend_task_generator = self._generator_wrapper(comprehend_generator)
  
  def start_geneate_outline(self, *args):
    outline_generator = outline_generate(*args)
    self.outline_generator = self._generator_wrapper(outline_generator)
  
  def start_generate_document(self, *args):
    doc_generator = article_generate(*args)
    self.doc_generator = self._generator_wrapper(doc_generator)
  
  def start_expand_doc(self, *args):
    expand_doc_generator = expand_doc_generate(*args)
    self.expand_doc_generator = self._generator_wrapper(expand_doc_generator)

  
  def _run(self, config, files=None):
    print("task {}: 开始运行...".format(self.id))
  
    prompt = config["article_prompt"]["content"]
    
    if self.search_needed:
      search_keywords = extract_search_keywords(prompt)
      # self._search_internet(search_keywords, config)
      time.sleep(0.3)
      self.search_result = {}
      self.search_ready = True
      print("task {}: 搜索完毕".format(self.id))
    
    if self.network_RAG_search_needed:
      # self._search_network_RAG(search_keywords)
      time.sleep(0.3)
      self.network_RAG_search_result = {}
      self.network_RAG_search_ready = True
      print("task {}: 远程RAG检索完毕".format(self.id))
      
    if self.local_RAG_search_needed and files:
      # self._search_local_RAG(files, prompt)
      time.sleep(0.3)
      self.local_RAG_search_result = {}
      self.local_RAG_search_ready = True
      print("task {}: 本地支持库检索完毕".format(self.id))
    
    self.search_ended = True
  
  def _search_internet(self, search_keywords: list[str], config: dict):
    if (config["search_engine"] == 'google'):
      self.search_result = do_google_serp_search(search_keywords, config)
    elif(config["search_engine"] == 'edge'):
      pass
    elif(config["search_engine"] == "baidu"):
      pass
  
  def _search_network_RAG(self, search_keywords: list[str], urls: list[str]=[]):
    self.network_RAG_search_result = do_tavily_ai_search(search_keywords, options={
      "urls_included": urls
    })
  
  def _search_local_RAG(self, files, query, result_count=4):
    documents_searched = do_local_RAG_search_by_files(files, query, result_count)
    self.local_RAG_search_result = [doc.page_content for doc in documents_searched]

  # def _clear(self):
  #   """
  #   Clear the task when target is generated totally.
  #   After clearing, you can still get all results the task has generated by the reference to it, 
  #   or call `xx_generator()` to re-generate `xx` by the search has done in the current task.
  #   But the task actually has been expunged from the tasks queue.
  #   """
  #   pass
  #   _tasks.remove(self)

  def _generator_wrapper(self, generator):
    """
    Receive the result_generator of the current task, and return the generator itself, except that the generator will do things additionally:
    1. save the result generated to task instance.
    """
    self.task_result = '' # initially it is an empty str
    self.generate_status = 'doing'
    for result in generator:
      # save the result
      self.task_result += result
      yield result
      
    # mark the task as generate_status.
    self.generate_status = 'done'
  
  def to_dict(self):
    return {
      "id": self.id,
      "config_id": self.config_id,
      "step_n": self.step_n,
      "generate_status": self.generate_status,
      "user_input": self.user_input,
      "task_result": self.task_result,
      "search_needed": self.search_needed,
      "network_RAG_search_needed": self.network_RAG_search_needed,
      "local_RAG_search_needed": self.local_RAG_search_needed,
      "search_ready": self.search_ready,
      "network_RAG_search_ready": self.network_RAG_search_ready,
      "local_RAG_search_ready": self.local_RAG_search_ready,
      "search_ended": self.search_ended,
    }