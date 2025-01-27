import time

def outline_generate(*args):
  # search_result, network_RAG_search_result, local_RAG_search_result = args
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' first', ' outline!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()