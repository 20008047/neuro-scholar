import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# 初始化配置：设置模型为 Gemini 1.5 Pro
def init_settings(api_key):
    os.environ["GOOGLE_API_KEY"] = api_key
    # model_name 选 gemini-1.5-pro，因为它窗口大，适合读论文
    Settings.llm = Gemini(model_name="models/gemini-1.5-flash", temperature=0.1)
    Settings.embedding = GeminiEmbedding(model_name="models/text-embedding-004")

# 处理上传的文件并保存到本地临时目录
def save_uploaded_file(uploaded_file, save_dir="./data"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# 核心函数：读取data文件夹下的所有文件，建立索引（知识库）
def get_index(data_dir="./data", storage_dir="./storage"):
    # 如果没有 storage 文件夹，说明是第一次运行，或者被清空了
    if not os.path.exists(storage_dir):
        # 检查 data 文件夹里有没有书，如果没有，返回空
        if not os.path.exists(data_dir) or not os.listdir(data_dir):
            return None
        
        # 读取文档
        documents = SimpleDirectoryReader(data_dir).load_data()
        # 建立索引
        index = VectorStoreIndex.from_documents(documents)
        # 保存索引到硬盘
        index.storage_context.persist(persist_dir=storage_dir)
        return index
    else:
        # 如果已经有索引，直接加载，速度快
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        return index

# 清空数据库（删除所有文件和索引）
def clear_database(data_dir="./data", storage_dir="./storage"):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir) # 删除文件夹及内容
        os.makedirs(data_dir)   # 重建空文件夹
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)