from baidusearch.baidusearch import search
 
def do_baidu_search(keyword: str, config=[]):
  try:
    results = search(keyword=keyword)
    return results
  except Exception as e:
    print(e)
    return None