import streamlit as st
import os
from utils import init_settings, save_uploaded_file, get_index, clear_database

st.set_page_config(page_title="NeuroScholar - Kimi版", layout="wide")
st.title("🌙 NeuroScholar (Powered by Kimi)")

with st.sidebar:
    st.header("⚙️ 设置与管理")
    
    # 获取 API Key
    if "MOONSHOT_API_KEY" in st.secrets:
        api_key = st.secrets["MOONSHOT_API_KEY"]
        st.success("Kimi API Key 已加载 ✅")
    else:
        api_key = st.text_input("请输入 Kimi API Key (sk-...)", type="password")

    st.divider()
    
    st.subheader("📄 上传文献")
    # 支持 PDF 和 TXT
    uploaded_files = st.file_uploader("选择文献", accept_multiple_files=True, type=['pdf', 'txt'])
    
    if st.button("开始处理/更新知识库"):
        if not api_key:
            st.error("请先填入 Kimi API Key！")
        elif not uploaded_files:
            st.warning("请先选择文件！")
        else:
            with st.spinner("正在启动 Kimi 并解析文献（首次运行可能需要下载模型）..."):
                init_settings(api_key)
                for up_file in uploaded_files:
                    save_uploaded_file(up_file)
                
                # 强制重建索引
                if os.path.exists("./storage"):
                    import shutil
                    shutil.rmtree("./storage")
                
                st.session_state.index = get_index()
                st.success(f"成功处理 {len(uploaded_files)} 篇文献！")

    st.divider()
    if st.button("🗑️ 清空库"):
        clear_database()
        if "index" in st.session_state:
            del st.session_state.index
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是基于 Kimi 长文本模型的科研助手。请上传论文，我能帮你总结实验方法和结论。"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("请输入问题..."):
    if not api_key:
        st.error("请先配置 API Key")
        st.stop()
    
    if "index" not in st.session_state:
        # 尝试静默加载
        try:
            init_settings(api_key)
            idx = get_index()
            if idx:
                st.session_state.index = idx
            else:
                st.info("请先上传文献。")
                st.stop()
        except:
             st.info("请先上传文献。")
             st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Kimi 正在阅读..."):
            chat_engine = st.session_state.index.as_chat_engine(
                chat_mode="condense_plus_context",
                verbose=True,
                system_prompt="你是一名神经科学专家。请基于上下文回答问题。回答要专业、准确，引用具体的实验数据。"
            )
            response = chat_engine.chat(prompt)
            st.markdown(response.response)
            
    st.session_state.messages.append({"role": "assistant", "content": response.response})