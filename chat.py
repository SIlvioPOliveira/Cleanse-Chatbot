import os
from dotenv import load_dotenv

# Imports atualizados para a nova versão do LangChain
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Carrega as variáveis de ambiente
load_dotenv()

# --- Configurações ---
DB_FAISS_PATH = "faiss_index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gemini-2.5-pro"

def main():
    """Função principal para o chatbot RAG com a lógica moderna do LangChain."""
    
    # Verifica se o "cérebro" da IA existe
    if not os.path.exists(DB_FAISS_PATH):
        print(f"ERRO: Banco de dados vetorial '{DB_FAISS_PATH}' não encontrado.")
        print("Por favor, execute o script 'create_vector_store.py' primeiro.")
        return

    print("Iniciando o sistema de chat com RAG (versão moderna)...")

    # 1. Carregar os componentes de busca (retriever)
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 4})
    print("Componentes de busca carregados.")

    # 2. Definir o template do prompt
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

    # 3. Configurar o LLM
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME)

    # 4. Montar a cadeia RAG usando a sintaxe LCEL (o "pipe" |)
    # Esta é a parte que substitui as funções antigas
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("--------------------------------------------------")
    print("Cadeia RAG pronta. Você já pode fazer suas perguntas.")
    print("--------------------------------------------------")

    # 5. Iniciar o loop de conversação
    while True:
        query = input("Você: ")
        if query.lower() in ['sair', 'exit', 'quit']:
            print("Volte sempre!")
            break
        if not query:
            continue
            
        # Invocar a nova cadeia
        answer = rag_chain.invoke(query)
        
        print("\nAssistente:", answer)
        
        # Opcional: Para ver as fontes, teríamos que modificar a cadeia um pouco,
        # mas por agora, vamos focar em fazer a resposta funcionar.

        print("--------------------------------------------------")

if __name__ == "__main__":
    main()