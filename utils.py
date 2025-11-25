import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai

def init_settings(api_key):
    # 1. 强制配置 Google 库
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    
    # 2. 【关键修改】使用 "models/gemini-1.5-flash-latest"
    # 加上 "-latest" 后缀通常能解决 404 找不到模型的问题
    Settings.llm = Gemini(
        model_name="models/gemini-1.5-flash-latest", 
        temperature=0.1
    )
    
    # Embedding 模型保持不变
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
        
        try:
            documents = SimpleDirectoryReader(data_dir).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=storage_dir)
            return index
        except Exception as e:
            # 如果读取出错，打印一下，防止直接崩网页
            print(f"Error building index: {e}")
            return None
    else:
        try:
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            index = load_index_from_storage(storage_context)
            return index
        except:
            # 如果索引坏了，返回None，强制重建
            return None

def clear_database(data_dir="./data", storage_dir="./storage"):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)