from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_core.documents import Document

from .tools import split_document_by_paragraph

from typing import Optional

if __name__ == '__main__':
  # For testing. Secret keys are needed for model creating
  from dotenv import load_dotenv
  load_dotenv()

qianfanModel = QianfanEmbeddingsEndpoint(
    model="Embedding-V1",
)

# todo: change vector store
vector_store = InMemoryVectorStore(embedding=qianfanModel)


def add_document(docs: str, metadata: dict):
  paragraphs = split_document_by_paragraph(docs)
  documents=[Document(page_content=text, metadata=metadata) for text in paragraphs]
  # print(documents)
  vector_store.add_documents(documents)

def RAG_search(query, k=4, filter: Optional[dict] = None) -> list[Document]:
  """
    use similarity_search to find top K quantity's documents
  """
  docs = vector_store.similarity_search(query, k, filter=filter)
  return docs

def do_local_RAG_search_by_files(files: list[dict], prompt: str, k=4):
  """
    Do RAG retrival by files given.
    One file is a dict has two keys: {"file_name", "file_data", "config_id"}
  """
  for file in files:
    file_name = file["file_name"]
    file_content = file["file_data"].decode('utf-8')
    config_id = file["config_id"]
    
    metadata = {
      "file_name": file_name,
      "config_id": config_id
    }
    add_document(file_content, metadata)
    RAG_result = RAG_search(prompt, k)
    return RAG_result




if __name__ == '__main__':
  add_document("""
  Embedding-V1是基于百度文心大模型技术的文本表示模型，将文本转化为用数值表示的向量形式，用于文本检索、信息推荐、知识挖掘等场景。本文介绍了相关API，本接口不限制商用。
  接口描述
  根据输入内容生成对应的向量表示。
  在线调试
  平台提供了 API在线调试平台-示例代码 ，用于帮助开发者调试接口，平台集成快速检索、查看开发文档、查看在线调用的请求内容和返回结果、复制和下载示例代码等功能，简单易用，更多内容请查看API在线调试介绍。
  """
  )
  res = RAG_search("平台提供了什么", k=1)
  print(res)