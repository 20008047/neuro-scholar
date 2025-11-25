import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
# 引入 OpenAI 库（Kimi 兼容 OpenAI 协议）
from llama_index.llms.openai import OpenAI
# 引入本地免费的嵌入模型
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_settings(api_key):
    # 1. 配置 Kimi (Moonshot AI)
    # 【关键修改】：手动指定 context_window 和 关闭 function calling
    # 这样 LlamaIndex 就不会去查白名单了，直接信任我们输入的参数
    Settings.llm = OpenAI(
        model="moonshot-v1-128k", 
        api_key=api_key, 
        api_base="https://api.moonshot.cn/v1",
        temperature=0.3,
        context_window=128000,        # <--- 手动告诉它：我有128k的记忆
        is_function_calling_model=False # <--- 告诉它：别检查函数调用功能，防报错
    )
    
    # 2. 配置嵌入模型 (Embedding)
    # 使用 HuggingFace 本地模型
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def save_uploaded_file(uploaded_file, save_dir="./data"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def get_index(data_dir="./data", storage_dir="./storage"):
    try:
        # 如果已有索引，直接加载
        if os.path.exists(storage_dir):
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            index = load_index_from_storage(storage_context)
            return index
            
        # 如果没有索引，且 data 文件夹有文件，则新建
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            return None
            
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=storage_dir)
        return index
            
    except Exception as e:
        print(f"Index Error: {e}")
        return None

def clear_database(data_dir="./data", storage_dir="./storage"):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)