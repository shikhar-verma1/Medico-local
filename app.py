import streamlit as st 
from rag_pipeline import medical_ai
import os

st.set_page_config("Medico-AI Assistant",page_icon="🩺",layout ="centered")
st.title("Private Medical AI Assitant")
st.caption("Powered by Phi-3 ,ChromaDB,and LangChain")

@st.cache_resource
def load_engine():
    return medical_ai()
qa_chain ,chat_history_db = load_engine()

with st.sidebar:
    st.header("DashBoard Controls")
    st.subheader("Upload the file")
    uploaded_file = st.file_uploader("upload a PDF file",type=["pdf"])
    
    if uploaded_file is not None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        records_dir = os.path.abspath("patient_records")
        os.makedirs(records_dir, exist_ok=True)
        
        save_path = os.path.join(records_dir, uploaded_file.name)
        
        with open(save_path,"wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"successfully uploaded {uploaded_file.name}")
        
        if st.button("process new pdf & restart AI"):
            st.cache_resource.clear()
            st.rerun()
            
    st.markdown("---")

    st.subheader(" Memory Management")
    st.markdown("Start a new patient session by wiping the AI current memory")
    if st.button("Clear Chat History"):
        chat_history_db.clear()
        st.rerun()
    
    
for msg in chat_history_db.messages:
    role ="user" if msg.type =="human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

if prompt :=st.chat_input("Ask question about the medical record"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing records..."):
            response =qa_chain.invoke({"query":prompt})
            final_text = response.get("answer",response.get("result", "Error: Could not find the text."))
            st.markdown(final_text)

