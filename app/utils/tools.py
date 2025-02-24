from .AImodels.erniebot import erniebot
from .AImodels.duckduckgo import ddgs
from typing import Iterator

def extract_model_name(model: str | None) -> str:
  model_used = None
  if model == None or model == 'erniebot':
    model_used = 'erniebot'
  elif model_used == 'gpt':
    model_used = 'gpt-4o-mini'
  elif model_used == 'claude':
    model_used = 'claude-3-haiku'
  elif model_used == 'deepseek':
    model_used = 'deepseek'
  
  return model_used

def send_message_to_model(sys_prompt, user_prompt, model_used) -> Iterator:
  if model_used == 'erniebot':
    response = erniebot.ChatCompletion.create(model="ernie-4.0",
                                          messages=[
                                            {"role": "user", "content": user_prompt}
                                          ],
                                          system=sys_prompt,
                                          stream=True)
    def generate():
      for chunk in response:
          result = chunk.get_result()
          yield f"{result}"
    return generate()
  else:
    response = ddgs.chat_yield(user_prompt, model=model_used)
    def generate():
      for chunk in response:
          result = chunk
          yield f"{result}"
    return generate()