from ..erniebot import erniebot
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
  from app.article_generate.task_manager import Task

sysprompt = """
You are an excellent GPT for article generation in **Chinese**.
You will generate an outline based on the user's reqirement.
"""

def outline_generate(task: "Task", *args):
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
    
    
  import time
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' comprehend', ' document!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()
    
  
  def generate():
    response = erniebot.ChatCompletion.create(model="ernie-4.0",
                                              messages=[
                                                {"role": "user", "content": prompt}
                                              ],
                                              system=sysprompt,
                                              stream=True)
    for chunk in response:
      result = chunk.get_result()
      yield f"{result}"
  return generate()