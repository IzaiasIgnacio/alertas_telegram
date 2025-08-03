from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
import yagmail
import os
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")

email_origem = os.getenv("EMAIL_ORIGEM")
email_senha = os.getenv("EMAIL_SENHA")
email_destino = os.getenv("EMAIL_DESTINO")

palavras_chave = ["q800d", "q800f", "s25"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares"]

yag = yagmail.SMTP(email_origem, email_senha)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

@client.on(events.NewMessage(chats=canais_monitorados))
async def handler(event):
    texto = event.raw_text
    if any(p.lower() in texto.lower() for p in palavras_chave):
        print(f"🔔 Palavra-chave detectada: {texto}")
        yag.send(to=email_destino, subject="🔔 Alerta do Telegram", contents=texto)

def start_bot():
    client.start()
    yag.send(to=email_destino, subject="🤖 Bot Iniciado", contents="O bot de alertas está rodando!")
    print("🤖 Bot iniciado...")
    client.run_until_disconnected()

# Web server para manter online
app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot está rodando!"

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
