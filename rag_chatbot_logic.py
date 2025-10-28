# rag_chatbot_logic.py (Versão V5 - Personalidade, Sem Memória, 100% Estável)

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Usamos apenas as ferramentas mais modernas e estáveis
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class RAGChatbot:
    def __init__(self):
        # --- Configurações ---
        DB_FAISS_PATH = "faiss_index"
        MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        LLM_MODEL_NAME = "gemini-2.5-pro"

        print("Carregando componentes do chatbot RAG (V5 com Personalidade)...")
        
        # Carregamento dos componentes
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        self.retriever = db.as_retriever(search_kwargs={'k': 4})
        self.llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=os.getenv("GOOGLE_API_KEY"))

        # --- NOVA LÓGICA DE PROMPT (PERSONALIDADE) ---
        
        # Este é o nosso novo prompt de resposta, que dá personalidade ao bot
        qa_prompt = ChatPromptTemplate.from_template(
            "Você é o 'Cleanse Chatbot', um especialista amigável e prestativo em League of Legends. Seu conhecimento vem de discussões em fóruns do Reddit."
            "Sua missão é ajudar os jogadores respondendo às perguntas deles de forma conversacional e natural, como se estivesse conversando com um amigo."
            "Use as informações do contexto abaixo para formular sua resposta."
            "Se a informação não estiver no contexto, diga algo natural como: 'Hmm, procurei aqui nos meus dados do Reddit, mas não encontrei uma resposta direta para isso. Posso tentar ajudar com outra coisa?'"
            "Nunca invente informações que não estão no contexto.\n\n"
            "Contexto:\n{context}\n\n"
            "Pergunta: {question}\n\n"
            "Resposta:"
        )

        # --- CADEIA RAG SIMPLES E ESTÁVEL (SEM MEMÓRIA) ---
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("Chatbot RAG (V5 com Personalidade) pronto.")

    def get_response(self, channel_id, query):
        if not query:
            return "Por favor, faça uma pergunta."
        
        # Invoca a cadeia simples, sem passar histórico
        answer = self.rag_chain.invoke(query)
        
        # OBS: Para adicionar as fontes, a cadeia precisaria de um pequeno ajuste,
        # mas por agora, o mais importante é ter uma resposta natural e estável.
        return answer