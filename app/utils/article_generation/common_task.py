from ..tools import extract_model_name, send_message_to_model
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
  from app.article_generate.task_manager import Task

sysprompt = """
You are an excellent GPT for article generation in **Chinese**.
You will generate the output based on the user's reqirement.
"""

def common_task_generate(task: "Task", *args):
  if task.user_input:
    prompt = task.user_input
  else: 
    article_title = task.article_title
    search_result = json.dumps(task.search_result, ensure_ascii=False)
    if task.network_RAG_search_result:
      network_RAG_search_result = json.dumps(task.network_RAG_search_result[0]["answer"], ensure_ascii=False)
    local_RAG_search_result = task.local_RAG_search_result
    
    prompt = """
    Please generate an outline, with these information given:
    
    The article tiltle is: {article_title};
    Related web search result(json format): {search_result};
    Related network RAG search result(json format): {network_RAG_search_result};
    Related network RAG search result: {local_RAG_search_result};
    
    If one of them is Null, just skip.
    Just list the outline,** in Chinese**.
    
    """.format(article_title=article_title, search_result=search_result, network_RAG_search_result=network_RAG_search_result, local_RAG_search_result=local_RAG_search_result)
    
  model_used = extract_model_name(task.model_used)
    
  import time
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' common', ' document!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()
  
  return send_message_to_model(sys_prompt=sysprompt, user_prompt=prompt, model_used=model_used)
