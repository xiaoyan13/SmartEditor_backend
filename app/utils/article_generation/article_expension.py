import time

def expand_doc_generate():
  def generate():
    doc = ['Hello', ' world!', ' This', ' is', ' the', ' second', ' document!']
    for str in doc:
      time.sleep(0.3)
      yield str
  return generate()