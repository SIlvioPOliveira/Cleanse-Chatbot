# discord_bot.py

import os
import discord
import httpx  # Biblioteca para fazer requisições HTTP
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = "http://127.0.0.1:8000/ask"  # O endereço do nosso "Cérebro" (FastAPI)

# --- Configuração do Bot do Discord (muito mais simples) ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print('-----------------------------------------')
    print(f'Logado com sucesso como {bot.user}')
    print('O bot está online e pronto para fazer pedidos à API!')
    print('-----------------------------------------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        query = message.content.replace(f'<@{bot.user.id}>', '').strip()

        if not query:
            await message.channel.send("Olá! Faça-me uma pergunta sobre League of Legends.")
            return
        
        thinking_message = await message.channel.send("🧠 Enviando sua pergunta para o cérebro da IA...")

        try:
            # Usamos um 'client' para fazer a requisição para nossa API FastAPI
            async with httpx.AsyncClient(timeout=120.0) as client: # Timeout de 120s
                # Faz o "pedido" para o garçom (FastAPI)
                response = await client.post(API_URL, json={"query": query, "channel_id": str(message.channel.id)})
                response.raise_for_status() # Lança um erro se a API retornar um status de erro
                
                # Pega o "prato pronto" (a resposta)
                data = response.json()
                answer = data.get("answer", "Não recebi uma resposta válida da IA.")
            
            await thinking_message.edit(content=answer)

        except httpx.RequestError as e:
            print(f"Erro de conexão com a API: {e}")
            await thinking_message.edit(content="Desculpe, não consegui me conectar ao cérebro da IA. Tente novamente mais tarde.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            await thinking_message.edit(content="Desculpe, ocorreu um erro inesperado ao processar sua pergunta.")

# --- Ponto de partida ---
if __name__ == "__main__":
    if not TOKEN:
        print("ERRO: O DISCORD_TOKEN não foi encontrado no arquivo .env!")
    else:
        print("Iniciando o bot do Discord (o 'Rosto')...")
        bot.run(TOKEN)