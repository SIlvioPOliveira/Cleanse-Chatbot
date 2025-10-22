import sqlite3
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DB_FILE = "reddit_rag_data.db"
DB_FAISS_PATH = "faiss_index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_posts_from_db(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    print(f"Carregando posts do banco de dados '{db_file}'...")
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()
    
    documents = []
    for post in posts:
        page_content = (f"Title: {post['title']}\n\nContent: {post['content']}\n\n--- Comments ---\n{post['comments_content']}")
        metadata = {"source": post['url'], "subreddit": post['subreddit']}
        documents.append(Document(page_content=page_content, metadata=metadata))
        
    print(f"Carregados {len(documents)} documentos.")
    return documents

def main():
    if not os.path.exists(DB_FILE):
        print(f"ERRO: Banco de dados '{DB_FILE}' não encontrado. Execute o 'reddit_researcher.py' primeiro.")
        return
        
    if os.path.exists(DB_FAISS_PATH):
        print(f"Removendo banco de dados vetorial antigo...")
        shutil.rmtree(DB_FAISS_PATH)

    documents = load_posts_from_db(DB_FILE)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    print(f"Documentos quebrados em {len(chunks)} chunks.")

    print(f"Carregando modelo de embedding '{MODEL_NAME}'...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    print("Criando o banco de dados vetorial com FAISS...")
    db = FAISS.from_documents(chunks, embeddings)
    
    db.save_local(DB_FAISS_PATH)
    print(f"Banco de dados vetorial salvo com sucesso em '{DB_FAISS_PATH}'!")

if __name__ == "__main__":
    main()