import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
try:
    from langchain.vectorstores import FAISS
except ImportError:
    FAISS = None
import pickle

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai")

VECTOR_DB_PATH = "/tmp/faiss_index/"
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

def get_embeddings():
    if EMBEDDING_MODEL == "openai":
        return OpenAIEmbeddings()
    else:
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_policy_document(doc, user_id):
    text = doc.content
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(text)
    metadatas = [{"doc_id": doc.id, "user_id": user_id, "chunk_id": i, "filename": doc.filename} for i in range(len(chunks))]
    if FAISS is None:
        print("FAISS is not installed or failed to load. Skipping index saving.")
        return
    embeddings = get_embeddings()
    vectordb = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
    # Save index per user
    vectordb.save_local(os.path.join(VECTOR_DB_PATH, f"faiss_{user_id}"))

def load_user_faiss(user_id):
    if FAISS is None:
        print("FAISS is not installed or failed to load. Skipping index retrieval.")
        return None
    embeddings = get_embeddings()
    index_path = os.path.join(VECTOR_DB_PATH, f"faiss_{user_id}")
    if not os.path.exists(index_path):
        return None
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
