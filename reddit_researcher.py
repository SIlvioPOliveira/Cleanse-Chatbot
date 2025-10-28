import praw
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = "script:BuscadorDeCampeoes:v1.0 (by /u/Ok-Interaction7332)"

SEARCH_TARGETS = {
    "Smolder": "SmolderMains",
    "Kayn": "KaynMains",
    "Jhin": "JhinMains", 
    "Ambessa": "AmbessaMains",
}

POST_LIMIT = 50
DB_FILE = "reddit_rag_data.db"
COMMENTS_LIMIT = 5
MIN_COMMENT_SCORE = 2

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, post_id TEXT UNIQUE, subreddit TEXT,
        champion_searched TEXT, title TEXT, content TEXT, comments_content TEXT,
        url TEXT, created_utc INTEGER, retrieved_at TIMESTAMP
    )
    """)
    conn.commit()
    return conn, cursor

def insert_post(cursor, conn, post_data):
    cursor.execute("""
    INSERT OR IGNORE INTO posts (post_id, subreddit, champion_searched, title, content, comments_content, url, created_utc, retrieved_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post_data['post_id'], post_data['subreddit'], post_data['champion_searched'],
        post_data['title'], post_data['content'], post_data['comments_content'],
        post_data['url'], post_data['created_utc'], post_data['retrieved_at']
    ))
    conn.commit()
    return cursor.rowcount > 0

print("Iniciando o script de coleta...")
conn, cursor = setup_database()
print(f"Banco de dados '{DB_FILE}' conectado/criado com sucesso.")

try:
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT, read_only=True)
    print("Autenticação com a API do Reddit bem-sucedida.")
except Exception as e:
    print(f"Erro na autenticação: {e}")
    exit()

total_posts_inserted = 0
for champion, subreddit_name in SEARCH_TARGETS.items():
    print(f"\n--- Buscando por '{champion}' em r/{subreddit_name} ---")
    try:
        subreddit = reddit.subreddit(subreddit_name)
        new_posts_in_loop = 0
        for post in subreddit.new(limit=POST_LIMIT):
            if champion.lower() in (post.title + " " + post.selftext).lower():
                post.comments.replace_more(limit=0)
                top_comments = sorted(post.comments, key=lambda c: c.score, reverse=True)
                
                formatted_comments = []
                for comment in top_comments:
                    if len(formatted_comments) < COMMENTS_LIMIT and comment.score >= MIN_COMMENT_SCORE and comment.author:
                        formatted_comments.append(f"Comentário (Score: {comment.score}): {comment.body}")
                
                post_data = {
                    "post_id": post.id, "subreddit": subreddit_name, "champion_searched": champion,
                    "title": post.title, "content": post.selftext, "comments_content": "\n\n---\n\n".join(formatted_comments),
                    "url": f"https://www.reddit.com{post.permalink}", "created_utc": int(post.created_utc),
                    "retrieved_at": datetime.now()
                }
                
                if insert_post(cursor, conn, post_data):
                    new_posts_in_loop += 1
        total_posts_inserted += new_posts_in_loop
        print(f"Análise concluída. {new_posts_in_loop} novo(s) post(s) inserido(s).")
    except Exception as e:
        print(f"ERRO ao processar r/{subreddit_name}: {e}.")
conn.close()
print(f"\n--- FIM DO SCRIPT ---\nTotal de {total_posts_inserted} novos posts adicionados.")