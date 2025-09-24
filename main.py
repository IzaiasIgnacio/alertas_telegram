from telethon import TelegramClient, events
from telethon.sessions import StringSession
import yagmail
import os
import asyncio
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

palavras_chave = ["q800d", "q800f", "astro bot"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares"]

yag = yagmail.SMTP(email_origem, email_senha)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

@client.on(events.NewMessage(chats=canais_monitorados))
async def handler(event):
    texto = event.raw_text
    if any(p.lower() in texto.lower() for p in palavras_chave):
        canal = event.chat.username or event.chat.title or "Canal desconhecido"
        print(f"🔔 Palavra-chave detectada no canal {canal}: {texto}")
        assunto = f"🔔 [{canal}] Alerta do Telegram"
        yag.send(to=email_destino, subject=assunto, contents=texto)


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        await client.start()
        yag.send(to=email_destino, subject="🤖 Bot Iniciado", contents="O bot de alertas está rodando!")
        print("🤖 Bot iniciado...")
        await client.run_until_disconnected()

    loop.run_until_complete(main())

# Web server para manter online
app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot está rodando!"

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
