# discord_bot.py

import os
import discord
import asyncio  # Importa a biblioteca para tarefas assíncronas
from dotenv import load_dotenv
from rag_chatbot_logic import RAGChatbot

# Carregar variáveis de ambiente, incluindo o token do bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- Configuração do Bot do Discord ---
intents = discord.Intents.default()
intents.message_content = True  # Ativa a permissão para ler o conteúdo das mensagens
bot = discord.Client(intents=intents)

# Cria uma instância da nossa lógica de chatbot
# Os modelos pesados são carregados apenas uma vez, quando o bot inicia.
print("Iniciando o bot do Discord...")
chatbot = RAGChatbot()

@bot.event
async def on_ready():
    """Evento que é chamado quando o bot se conecta com sucesso ao Discord."""
    print('-----------------------------------------')
    print(f'Logado com sucesso como {bot.user}')
    print('O bot está online e pronto para responder!')
    print('Me mencione em um canal para começar a conversar (ex: @MeuBot qual a build do Jhin?).')
    print('-----------------------------------------')

@bot.event
async def on_message(message):
    """Evento que é chamado sempre que uma mensagem é enviada em um canal que o bot pode ver."""
    # 1. Ignora mensagens enviadas pelo próprio bot para evitar loops infinitos
    if message.author == bot.user:
        return

    # 2. Verifica se o bot foi mencionado na mensagem
    if bot.user.mentioned_in(message):
        
        # 3. Limpa a menção da mensagem para obter a pergunta real do usuário
        query = message.content.replace(f'<@{bot.user.id}>', '').strip()

        if not query:
            await message.channel.send("Olá! Faça-me uma pergunta sobre League of Legends.")
            return
        
        # ID do canal para manter históricos de conversa separados
        channel_id = str(message.channel.id)

        # 4. Envia uma mensagem "Pensando..." para o usuário saber que o bot está trabalhando
        thinking_message = await message.channel.send("🧠 Analisando os dados do Reddit...")

        try:
            # 5. [CORREÇÃO] Executa a função demorada em uma thread separada para não bloquear o bot
            answer = await asyncio.to_thread(chatbot.get_response, channel_id, query)
            
            # 6. Edita a mensagem "Pensando..." com a resposta final
            await thinking_message.edit(content=answer)

        except Exception as e:
            print(f"Ocorreu um erro ao processar a pergunta: {e}")
            # Envia uma mensagem de erro mais detalhada no Discord
            await thinking_message.edit(content=f"Desculpe, ocorreu um erro ao processar sua pergunta.")

# --- Ponto de partida ---
if __name__ == "__main__":
    if not TOKEN:
        print("ERRO: O DISCORD_TOKEN não foi encontrado no arquivo .env!")
    else:
        # Inicia o bot usando o token
        bot.run(TOKEN)