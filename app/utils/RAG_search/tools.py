import re

def split_by_punctuation(text, punctuations):
    pattern = f"[{re.escape(punctuations)}]"
    result = re.split(pattern, text)
    return [item for item in result if item]


def split_by_length(text, length):
  result = []
  while len(text) > length:
    result.append(text[:length])
    text = text[length:]
  if text:
      result.append(text)


def split_document_by_paragraph(text: str):
    """
      convert a document string into list based on paragraphs
    """
    paragraphs = text.strip().split('\n')
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return paragraphs


def split_text(text, max_length=512):
    lines = text.strip().split('\n')
    
    result = []
    
    for line in lines:
      if len(line) <= max_length:
        result.append(line)
      else:
        # split by '.' '。‘
        sentences = split_by_punctuation(text=line, punctuations='。.')
        
        temp_texts_all = []
        for sentence in sentences:
          if len(sentence <= max_length):
            result.append(sentence)
          else:
            # split by comma
            temp_texts = split_by_punctuation(text=sentence, punctuations='，.')
            temp_texts_all += temp_texts
        
        for temp_text in temp_texts_all:
          if (len(temp_text) <= max_length):
            result.append(temp_text)
          else:
            # split by max length
            temp_chunks = split_by_length(text=text, length=max_length)
            result += temp_chunks
            
      return result
             
    