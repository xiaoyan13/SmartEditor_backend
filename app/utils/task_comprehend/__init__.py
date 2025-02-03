from ..erniebot import erniebot
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
  from app.article_generate.task_manager import Task


sysprompt = """
You are an excellent GPT for article generation.
The user will ask for your idea and thinking about how to write an article, with some information given(which is optional). You should do speculating and output your thinking about how to write the outline and article better, e.g. Output your thinking of what should be in attention.
Just tell the user your thinking, don't really generate any outline and article framework! Don't list things, output several paragraphs.
"""

def task_comprehend_generate(task: "Task", *args):
  article_title = task.article_title
  search_result = json.dumps(task.search_result, ensure_ascii=False)
  network_RAG_search_result = json.dumps(task.network_RAG_search_result[0]["answer"], ensure_ascii=False)
  local_RAG_search_result = task.local_RAG_search_result
  
  prompt = """
  Please trying to think as much as possible of how can I generate the article better, with these information given:
  
  The article tiltle is: {article_title};
  Related web search result(json format): {search_result};
  Related network RAG search result(json format): {network_RAG_search_result};
  Related network RAG search result: {local_RAG_search_result};
  
  If one of them is Null, just skip.
  Told me your understanding of this task, what and how will you do to generate, aiming to generate the outline better. 
  Ouput **must in Chinese**.
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