# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from rag_chatbot_logic import RAGChatbot

# Cria a aplicação FastAPI
app = FastAPI(
    title="Cleanse Chatbot API",
    description="Uma API para interagir com o chatbot RAG de League of Legends.",
    version="1.0.0",
)

# Cria uma instância única do nosso chatbot.
# Os modelos pesados são carregados apenas uma vez, quando a API inicia.
print("Carregando o modelo do chatbot RAG...")
chatbot = RAGChatbot()
print("Modelo carregado. A API está pronta para receber requisições.")

# Define o formato do corpo da requisição que esperamos receber
class QuestionRequest(BaseModel):
    query: str
    channel_id: str  # Mantemos para futura implementação de memória por canal

# Define o endpoint principal da nossa API
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Recebe uma pergunta, processa com o RAG e retorna a resposta.
    """
    # A lógica de resposta já existe na nossa classe RAGChatbot
    answer = chatbot.get_response(request.channel_id, request.query)
    
    # Retorna a resposta em um formato JSON
    return {"answer": answer}

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Cleanse Chatbot. Use o endpoint /ask para fazer perguntas."}