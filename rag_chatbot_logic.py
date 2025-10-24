# rag_chatbot_logic.py

import os
from dotenv import load_dotenv # Adicione este import
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Carrega as variáveis de ambiente DENTRO deste arquivo também
load_dotenv()

class RAGChatbot:
    def __init__(self):
        # --- Configurações ---
        DB_FAISS_PATH = "faiss_index"
        MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        LLM_MODEL_NAME = "gemini-2.5-pro"

        print("Carregando componentes do chatbot RAG...")
        
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_kwargs={'k': 4})

        prompt_template = """
        Você é um assistente especialista em League of Legends.
        Responda a pergunta do usuário baseando-se única e exclusivamente no contexto fornecido abaixo.
        Se a informação não estiver no contexto, diga "Com base nos dados que tenho, não encontrei uma resposta para isso."

        Contexto:
        {context}

        Pergunta:
        {question}

        Resposta:
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # ## A CORREÇÃO ESTÁ AQUI ##
        # 1. Lemos a chave da API do ambiente
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Chave GOOGLE_API_KEY não encontrada no arquivo .env")
            
        # 2. Passamos a chave diretamente para o construtor do LLM
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=api_key)

        self.rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("Chatbot RAG pronto.")

    def get_response(self, channel_id, query):
        if not query:
            return "Por favor, faça uma pergunta."
        
        return self.rag_chain.invoke(query)