import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.moonshot import Moonshot
from llama_index.embeddings.moonshot import MoonshotEmbedding


def init_settings(api_key):
    # 配置 Kimi (Moonshot)
    os.environ["MOONSHOT_API_KEY"] = api_key

    # 设置大语言模型
    Settings.llm = Moonshot(
        model="moonshot-v1-8k",
        api_key=api_key,
        temperature=0.1
    )

    # 设置文本嵌入模型
    Settings.embedding = MoonshotEmbedding(
        model="moonshot-v1-embed",
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
