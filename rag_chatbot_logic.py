# rag_chatbot_logic.py (Versão Simplificada - 1 Chamada de API por Pergunta)

import os
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class RAGChatbot:
    def __init__(self):
        # --- Configurações ---
        DB_FAISS_PATH = "faiss_index"
        MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        LLM_MODEL_NAME = "gemini-1.0-pro" # Usando o nome de modelo estável

        print("Carregando componentes do chatbot RAG (versão simplificada - 1 chamada)...")
        
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_kwargs={'k': 4})

        # O prompt agora é mais simples, pois não há histórico de conversa
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
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME)

        # A cadeia RAG volta a ser a mais simples e direta
        self.rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("Chatbot RAG (versão simplificada) pronto.")

    # A função agora só precisa do 'query' para funcionar.
    # Mantemos 'channel_id' aqui apenas para manter a compatibilidade com o discord_bot.py,
    # mas ele não será usado internamente.
    def get_response(self, channel_id, query):
        if not query:
            return "Por favor, faça uma pergunta."
        
        # A chamada é muito mais simples e faz apenas UMA requisição à API.
        return self.rag_chain.invoke(query)