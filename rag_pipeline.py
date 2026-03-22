from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
import shutil
import os
from langchain_community.llms import Ollama 
from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFDirectoryLoader

from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import SQLChatMessageHistory

def medical_ai():
    db_path = "./chroma_db"
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "patient_records")
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    loader = PyPDFDirectoryLoader(data_folder)
    raw_documents =  loader.load()
    print(f"\nDEBUG: successfully read {len(raw_documents)} pages from {data_folder}!\n")
    if len(raw_documents)==0:
        print("No PDF found! loading default placeholder")
        raw_documents = [Document(page_content="""No patient records found 
        in the directory. Please add PDF files.""")]

    text_splitter =RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 50
            )
    
    chunks = text_splitter.split_documents(raw_documents)
    print(f"created {len(chunks)} chunks")

    embeddings = OllamaEmbeddings(model = "mxbai-embed-large")
    vectorstore = Chroma.from_documents(chunks,embeddings,persist_directory="./chroma_db")
    
    chroma_retriever =vectorstore.as_retriever(search_kwargs = {"k":3})
    bm25retriever = BM25Retriever.from_documents(chunks)
    bm25retriever.k =3

    combined_retriever =EnsembleRetriever(
        retrievers = [chroma_retriever,bm25retriever],
        weights =[0.3,0.7]
    )
    llm = Ollama(model = "phi3")

    chat_history_db = SQLChatMessageHistory(
        session_id= "doctor_session_01",
        connection_string= "sqlite:///medical_chat_history.db"
    )
    memory = ConversationBufferMemory(
        memory_key = "chat_history",
        chat_memory =chat_history_db,
        return_message = True
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm =llm,
        retriever = combined_retriever,
        memory = memory 
    )
    return qa_chain, chat_history_db
    

        