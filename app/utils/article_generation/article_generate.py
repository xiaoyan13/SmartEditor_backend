from ..erniebot import erniebot
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
  from app.article_generate.task_manager import Task

sysprompt = """
You are an excellent GPT for article generation in **Chinese**.
You will generated an article based on the user's reqirement.
"""

def article_generate(task: "Task", *args):
  if task.user_input:
    prompt = task.user_input
  else: 
    article_title = task.article_title
    search_result = json.dumps(task.search_result, ensure_ascii=False)
    network_RAG_search_result = json.dumps(task.network_RAG_search_result[0]["answer"], ensure_ascii=False)
    local_RAG_search_result = task.local_RAG_search_result
    
    prompt = """
    Please generate an article, with these information given:
    
    The article tiltle is: {article_title};
    Related web search result(json format): {search_result};
    Related network RAG search result(json format): {network_RAG_search_result};
    Related network RAG search result: {local_RAG_search_result};
    
    If one of them is Null, just skip.
    Told me how will you generate the article,** in Chinese**.
    
    """.format(article_title=article_title, search_result=search_result, network_RAG_search_result=network_RAG_search_result, local_RAG_search_result=local_RAG_search_result)
    
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