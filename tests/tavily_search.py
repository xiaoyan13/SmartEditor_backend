"""
    python -m tests.tavily_search
"""

from app.utils.tavily_search import do_tavily_ai_search
import json
from os import path

current_workspace = path.dirname(path.abspath(__file__))
target_file = path.join(current_workspace, 'text.json')
print(target_file)

if __name__ == '__main__':
    res = do_tavily_ai_search(
        '你好，世界', 
        options={
            # 'urls_included': [
            #     'https://zh.wikipedia.org/wiki/Hello_World',
            # ]
        }
    )
    with open(target_file, 'w') as file:
        file.write(json.dumps(res[0], ensure_ascii=False, indent=2))