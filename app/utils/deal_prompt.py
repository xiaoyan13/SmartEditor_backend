from .erniebot import erniebot

prompt = """
You are expert linguist. Extract all the keywords from the given paragraph of text about artificial 
intelligence.

Paragraph: {text}

Constraints: Start with the delimiter ‘Keywords list:’ and limit the number of keywords to a maximum 
of five, still can less than five. Judge the appropriate count by yourself.**DO NOT output any tips or other sentences.**
"""

def extract_search_keywords(text: str):
  messages = [
    {"role": "user", "content": prompt.format(text=text)}
  ]
  response = erniebot.ChatCompletion.create(model="ernie-4.0",
                                            messages=messages,
                                            stream=False)
  keywords_string = response.get_result()
  # Extract the part after 'Keywords list:' and split it by commas
  keywords_part = keywords_string.split("Keywords list:")[1].strip()
  return [keyword.strip() for keyword in keywords_part.split(",")]


if __name__ == '__main__':
  res = extract_search_keywords("""
                          Keywords extraction is a natural language processing task which involves identifying the most relevant and informative words from the given text. These keywords are the terms that best describe the content of the given text. The main use of keywords is that they are useful for indexing and searching.
                          """)
  print(res)