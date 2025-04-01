from langchain.retrievers.multi_query import MultiQueryRetriever
from . import qianfanModel, vector_store
import logging

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

llm = qianfanModel

def retrieve_info_vector_store(question):
  retriever_from_llm = MultiQueryRetriever.from_llm(
      retriever=vector_store.as_retriever(), llm=llm
  )
  unique_docs = retriever_from_llm.invoke(question)
  return unique_docs