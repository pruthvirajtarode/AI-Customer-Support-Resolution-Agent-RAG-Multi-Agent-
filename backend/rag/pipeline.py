import os
import tempfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    FAISS = None
import pickle

VECTOR_DB_PATH = os.path.join(tempfile.gettempdir(), "faiss_index")
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Simplified VectorDB for Serverless Compatibility
class SimpleSimilarity:
    def __init__(self, texts, metadatas):
        self.texts = texts
        self.metadatas = metadatas
    def similarity_search(self, query, k=3):
        results = []
        q_words = query.lower().split()
        for i, text in enumerate(self.texts):
            score = sum(3 for w in q_words if w in text.lower())
            results.append((score, text, self.metadatas[i]))
        # Sort and return top k
        results.sort(key=lambda x: x[0], reverse=True)
        from langchain.schema import Document
        return [Document(page_content=r[1], metadata=r[2]) for r in results[:k]]

def process_policy_document(doc, user_id):
    text = doc.content
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(text)
    metadatas = [{"doc_id": doc.id, "user_id": user_id, "chunk_id": i, "filename": doc.filename} for i in range(len(chunks))]
    
    index_name = f"simple_index_{user_id}.pkl"
    index_path = os.path.join(VECTOR_DB_PATH, index_name)
    with open(index_path, "wb") as f:
        pickle.dump({"chunks": chunks, "metadatas": metadatas}, f)

def load_user_faiss(user_id):
    index_name = f"simple_index_{user_id}.pkl"
    index_path = os.path.join(VECTOR_DB_PATH, index_name)
    if not os.path.exists(index_path):
        return None
    try:
        with open(index_path, "rb") as f:
            data = pickle.load(f)
        return SimpleSimilarity(data["chunks"], data["metadatas"])
    except Exception:
        return None
