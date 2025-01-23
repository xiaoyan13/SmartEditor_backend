import time

def article_generate(*args):
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' first', ' document!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()