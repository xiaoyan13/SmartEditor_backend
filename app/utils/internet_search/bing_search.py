import requests
import os

search_url = "https://api.bing.microsoft.com/v7.0/search"

subscription_key = os.getenv('BING_TOKEN')

def do_bing_search(keyword: str, config=[]):
  headers = {"Ocp-Apim-Subscription-Key": subscription_key}
  params = {"q": keyword, "textDecorations": True, "textFormat": "HTML"}
  response = requests.get(search_url, headers=headers, params=params)
  response.raise_for_status()
  search_results = response.json()
  return search_results