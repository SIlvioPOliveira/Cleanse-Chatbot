# discord_bot.py (Versão V6 - Comandos de Barra /ask)

import os
import discord
import httpx
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = "http://127.0.0.1:8000/ask"

# --- Configuração do Bot do Discord (Adaptado para Comandos) ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ## MUDANÇA (COMANDOS) ##: Criamos uma "árvore de comandos" para o nosso cliente
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    # ## MUDANÇA (COMANDOS) ##: Sincroniza os comandos com o Discord
    # Isso faz com que o comando /ask apareça para os usuários.
    await tree.sync()
    print('-----------------------------------------')
    print(f'Logado com sucesso como {client.user}')
    print('Comandos sincronizados. O bot está pronto!')
    print('-----------------------------------------')

# ## MUDANÇA (COMANDOS) ##: Registramos o comando /ask
# O 'name' é o nome do comando, e 'description' é o texto de ajuda que aparece no Discord.
@tree.command(name="ask", description="Faça uma pergunta para o Cleanse Chatbot sobre League of Legends")
async def ask_command(interaction: discord.Interaction, question: str):
    """
    Esta função é chamada quando um usuário executa o comando /ask.
    'interaction' é o objeto que usamos para responder.
    'question' é o texto que o usuário digitou no comando.
    """
    # 1. Resposta imediata e "invisível" (defer)
    # Isso diz ao Discord: "Recebi o comando, estou trabalhando nisso, aguarde."
    # Se não fizermos isso, o Discord acha que o bot travou se a resposta demorar.
    await interaction.response.defer()

    try:
        # 2. Faz o "pedido" para a nossa API FastAPI (a mesma lógica de antes)
        async with httpx.AsyncClient(timeout=120.0) as http_client:
            response = await http_client.post(API_URL, json={"query": question, "channel_id": str(interaction.channel_id)})
            response.raise_for_status()
            
            data = response.json()
            answer = data.get("answer", "Não recebi uma resposta válida da IA.")
        
        # 3. Envia a resposta final
        # 'followup.send' é usado para enviar a resposta após o 'defer'
        await interaction.followup.send(content=answer)

    except httpx.RequestError as e:
        print(f"Erro de conexão com a API: {e}")
        await interaction.followup.send(content="Desculpe, não consegui me conectar ao cérebro da IA. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        await interaction.followup.send(content="Desculpe, ocorreu um erro inesperado ao processar sua pergunta.")

# --- Ponto de partida (sem mudanças) ---
if __name__ == "__main__":
    if not TOKEN:
        print("ERRO: O DISCORD_TOKEN não foi encontrado no arquivo .env!")
    else:
        print("Iniciando o bot do Discord (o 'Rosto')...")
        client.run(TOKEN)