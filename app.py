import streamlit as st
import os
from utils import init_settings, save_uploaded_file, get_index, clear_database

# 1. 页面基础设置
st.set_page_config(page_title="NeuroScholar - 神经科学科研助手", layout="wide")
st.title("🧠 NeuroScholar: 您的专属科研文献库")

# 2. 侧边栏：设置与上传
with st.sidebar:
    st.header("⚙️ 设置与管理")
    
    # 获取 API Key：优先从云端机密获取，如果没有，则让用户输入
    # 这样既方便部署，也方便本地测试
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("API Key 已从系统配置加载 ✅")
    else:
        api_key = st.text_input("请输入 Google API Key", type="password")

    st.divider()
    
    # 文件上传区
    st.subheader("📄 上传文献 (PDF或TXT)")
    uploaded_files = st.file_uploader("选择文献（PDF或TXT）", accept_multiple_files=True, type=['pdf','txt'])
    
    if st.button("开始处理/更新知识库"):
        if not api_key:
            st.error("请先配置 API Key！")
        elif not uploaded_files:
            st.warning("请先选择 PDF 文件！")
        else:
            with st.spinner("正在解析神经科学文献，请稍候..."):
                # 初始化模型
                init_settings(api_key)
                # 保存所有文件
                for up_file in uploaded_files:
                    save_uploaded_file(up_file)
                # 触发重建索引
                # 为了简单起见，这里我们清除旧索引重新构建，确保没有残留
                # 生产环境可以用增量更新，但科研个人用全量更新更稳
                if os.path.exists("./storage"):
                    import shutil
                    shutil.rmtree("./storage")
                
                # 重新获取索引
                st.session_state.index = get_index()
                st.success(f"成功处理 {len(uploaded_files)} 篇文献！")

    st.divider()
    if st.button("🗑️ 清空所有文献库"):
        clear_database()
        if "index" in st.session_state:
            del st.session_state.index
        st.warning("文献库已清空")
        st.rerun()

# 3. 主界面：聊天区域
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是专精于神经科学的 AI 助手。请上传 PDF，然后问我关于实验方法、结论或综述的问题。"}
    ]

# 显示历史聊天记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. 处理用户提问
if prompt := st.chat_input("请输入您的问题..."):
    # 检查 Key
    if not api_key:
        st.error("请先在侧边栏配置 Google API Key")
        st.stop()
    
    # 检查是否有索引（知识库）
    if "index" not in st.session_state:
        # 尝试加载一下，万一之前处理过
        try:
            init_settings(api_key)
            loaded_index = get_index()
            if loaded_index:
                st.session_state.index = loaded_index
            else:
                st.info("请先上传文献并点击‘开始处理’。")
                st.stop()
        except:
             st.info("请先上传文献并点击‘开始处理’。")
             st.stop()

    # 显示用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 生成回答
    with st.chat_message("assistant"):
        with st.spinner("正在检索文献并思考..."):
            # 建立聊天引擎
            chat_engine = st.session_state.index.as_chat_engine(
                chat_mode="condense_plus_context",
                verbose=True,
                system_prompt="""你是一位世界顶尖的神经科学博士后助手。
                你的回答必须基于我上传的文献内容。
                - 如果问及实验方法，请列出具体的参数（如病毒滴度、坐标、刺激频率）。
                - 如果问及结论，请引用具体的 Figure 或实验结果。
                - 如果文献中没有提到，请直接说“文献中未找到相关信息”，不要编造。
                """
            )
            response = chat_engine.chat(prompt)
            st.markdown(response.response)
            
    # 保存助手回答
    st.session_state.messages.append({"role": "assistant", "content": response.response})