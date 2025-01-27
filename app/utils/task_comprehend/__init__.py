import time

def task_comprehend_generate(*args):
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' first', ' task!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()