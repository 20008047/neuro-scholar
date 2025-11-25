import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai

def init_settings(api_key):
    # 1. 强制配置 API Key
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    
    # 2. 【修正】根据您的截图，启用 Gemini 3 Pro
    # 我们尝试标准命名格式
    try:
        Settings.llm = Gemini(
            model_name="models/gemini-3.0-pro", 
            temperature=0.1
        )
    except:
        # 如果带前缀不行，尝试不带前缀，或者尝试 2.5 Pro 作为备选
        # 但主要目标是 3.0
        print("尝试 models/gemini-3.0-pro 失败，尝试 gemini-3.0-pro")
        Settings.llm = Gemini(
            model="gemini-3.0-pro", 
            api_key=api_key,
            temperature=0.1
        )

    # 3. 嵌入模型更新
    # 既然有 3.0 模型，Embedding 可能也更新了，但为了稳妥我们先用通用的 text-embedding-004
    # 如果报错，可以尝试 models/text-embedding-005 (如果有的话)
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
    try:
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
    except Exception as e:
        print(f"Index Error: {e}")
        return None

def clear_database(data_dir="./data", storage_dir="./storage"):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)