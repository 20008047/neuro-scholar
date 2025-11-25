import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai

# 初始化配置
def init_settings(api_key):
    # 1. 直接配置 Google 底层库，防止环境读取失败
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    
    # 2. 修改模型名字：去掉 "models/" 前缀，直接用 "gemini-1.5-flash"
    # 这样可以避免双重前缀导致的 NotFound 错误
    # 同时显式传入 api_key
    Settings.llm = Gemini(
        model="gemini-1.5-flash", 
        api_key=api_key,
        temperature=0.1
    )
    
    # Embedding 模型也去掉前缀
    Settings.embedding = GeminiEmbedding(
        model_name="models/text-embedding-004", 
        api_key=api_key
    )

def save_uploaded_file(uploaded_file, save_dir="./data"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def get_index(data_dir="./data", storage_dir="./storage"):
    if not os.path.exists(storage_dir):
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            return None
        
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=storage_dir)
        return index
    else:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        return index

def clear_database(data_dir="./data", storage_dir="./storage"):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)