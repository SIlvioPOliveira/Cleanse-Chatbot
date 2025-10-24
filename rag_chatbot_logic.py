# rag_chatbot_logic.py (Versão V3.1 - Usando a sintaxe moderna LCEL)

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ## MUDANÇA (LCEL) ##: Importamos as novas ferramentas para a sintaxe moderna
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter # Ferramenta padrão do Python para pegar itens de um dicionário

load_dotenv()

class RAGChatbot:
    def __init__(self):
        # --- Configurações ---
        DB_FAISS_PATH = "faiss_index"
        MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        LLM_MODEL_NAME = "gemini-2.5-pro"

        print("Carregando componentes do chatbot RAG (V3.1 com Memória LCEL)...")
        
        # Carregamento dos componentes (sem mudanças)
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        self.retriever = db.as_retriever(search_kwargs={'k': 4})
        self.llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=os.getenv("GOOGLE_API_KEY"))

        # --- INÍCIO DA NOVA LÓGICA LCEL PARA MEMÓRIA ---

        # 1. Prompt para re-formular a pergunta
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Dada a conversa abaixo e a última pergunta, re-formule a pergunta para ser uma pergunta independente."),
                MessagesPlaceholder("chat_history"),
                ("human", "{question}"),
            ]
        )
        
        # 2. Cadeia que re-formula a pergunta
        history_aware_retriever_chain = (
            contextualize_q_prompt
            | self.llm
            | StrOutputParser()
            | self.retriever
        )
        
        # 3. Prompt final para gerar a resposta
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente especialista em League of Legends. Responda a pergunta do usuário baseando-se única e exclusivamente no contexto fornecido.\n\nContexto:\n{context}"),
                MessagesPlaceholder("chat_history"),
                ("human", "{question}"),
            ]
        )

        # 4. Monta a cadeia RAG completa usando LCEL
        self.rag_chain = (
            RunnablePassthrough.assign(
                context=RunnablePassthrough.assign(
                    chat_history=RunnableLambda(lambda x: x["chat_history"])
                )
                | contextualize_q_prompt
                | self.llm
                | StrOutputParser()
                | self.retriever
            )
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Dicionário para armazenar o histórico de cada canal
        self.chat_histories = {}
        
        print("Chatbot RAG (V3.1 com Memória LCEL) pronto.")

    def get_response(self, channel_id, query):
        if not query:
            return "Por favor, faça uma pergunta."
        
        if channel_id not in self.chat_histories:
            self.chat_histories[channel_id] = []
        
        chat_history = self.chat_histories[channel_id]

        # Invoca a nova cadeia LCEL
        answer = self.rag_chain.invoke({
            "question": query,
            "chat_history": chat_history
        })
        
        # Atualiza o histórico
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=answer))
        self.chat_histories[channel_id] = chat_history[-6:]
        
        # OBS: Para adicionar as fontes de volta, a cadeia precisaria de um pequeno ajuste,
        # mas por agora, o mais importante é fazer a resposta com memória funcionar.
        return answer