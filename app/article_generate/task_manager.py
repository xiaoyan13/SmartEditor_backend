import uuid
import weakref
import threading
import time

from database import db
from .models import ArticleConfig
from ..utils import do_tavily_ai_search, model_to_dict
from ..utils.deal_prompt import extract_search_keywords

"""
  Manager for article generation task.
"""

# task queue
_tasks: list["Task"] = []
# task id maps to task; use weakmap to avoid memory leakage
id_weak_map = weakref.WeakValueDictionary()

class Task:
  @staticmethod
  def get_tasks_by_config_id(config_id):
    result: list[Task] = []
    for task in _tasks:
      if task.config_id == config_id:
        result.append(task)
    return result
  
  @staticmethod
  def get_task_by_id(id) -> "Task":
    return id_weak_map.get(id)
  
  def __init__(self, config_id):
    self.id = str(uuid.uuid4())
    self.config_id = config_id
    _tasks.append(self)
    id_weak_map[self.id] = self
  
  id: str
  config_id: int # Every task has its corresponding article config_id.
  search_ready: bool = False
  network_RAG_search_ready: bool = False
  local_RAG_search_ready: bool = False
  document_ready: bool = False
  
  search_result = None
  network_RAG_search_result = None
  local_RAG_search_result = None
  document_str = None
  
  def run(self):
    """
    Run an article generation task.
    Considering the convenience, a task generates an entire article step by step sequentially:
    1. search the internet
    2. search the network RAG if setted
    3. search the local RAG if setted
    4. generate the article based on these result.
    
    Once `get_document()` called returns the entire document(not None) successfully, 
    `clear()` should be not be forgotten to call so that task can be expunged from the tasks queue and destroyed.
    """
    
    # 这里选择使用线程来 run task
    # Flask 并不考虑创建线程的情况，所以创建线程会导致 Flask 上下文丢失。这里先把 task 需要的配置拿到.
    config = db.session.get(ArticleConfig, self.config_id)
    config = model_to_dict(config)
    thread = threading.Thread(target=self._run, args=[config])
    thread.start()
    
  def get_status(self, status_wanted) -> bool:
    return getattr(self, status_wanted)
  
  def clear(self):
    """
    Clear the task. After clearing, you can still get all results the task have generated, by the reference to it, but the task will never be reused, and expunged from the tasks queue.
    """
    _tasks.remove(self)
  
  def get_document(self):
    # return "test_string"
    
    if self.document_ready:
      return self.document_str
    else:
      return None
    
  def _run(self, config):
    print("task {}: 开始运行...".format(self.id))
  
    net_RAG = config["networking_RAG"]
    local_RAG = config["local_RAG"]
    search_keywords = extract_search_keywords(config["article_prompt"]["content"])
    
    # self._search_internet(search_keywords)
    time.sleep(3)
    self.search_ready = True
    print("task {}: 搜索完毕".format(self.id))
    
    if net_RAG:
      # self._search_network_RAG(search_keywords, urls=[])
      time.sleep(3)
      self.network_RAG_search_ready = True
      print("task {}: 远程RAG检索完毕".format(self.id))
      
    if local_RAG:
      # self._search_local_RAG(self.config_id)
      time.sleep(3)
      self.local_RAG_search_ready = True
      print("task {}: 本地支持库检索完毕".format(self.id))
      
    # self._generate_document()
    time.sleep(3)
    self.document_ready = True
    print("task {}: 文章生成完毕".format(self.id))
    print(self.document_str)
  
  def _search_internet(self, search_keywords: list[str]):
    pass
  
  def _search_network_RAG(self, search_keywords: list[str], urls: list[str]):
    self.network_RAG_search_result = do_tavily_ai_search(search_keywords, options={
      "urls_included": urls
    })
  
  def _search_local_RAG(self):
    pass
  
  def _generate_document(self):
    pass

  def to_dict(self):
    return {
      "id": self.id,
      "config_id": self.config_id,
      "search_ready": self.search_ready,
      "network_RAG_search_ready": self.network_RAG_search_ready,
      "local_RAG_search_ready": self.local_RAG_search_ready,
      "document_ready": self.document_ready,
    }