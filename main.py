from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import os
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio

load_dotenv()

# 🔑 Credenciais do Telegram
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")

# 📧 Credenciais Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

# 📢 Configuração de canais e palavras-chave
palavras_chave = ["q800d", "q800f", "astro bot", "qned70", "b650f", "s70ty"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares"]


# Função de envio via Mailgun API
def enviar_email(subject, body):
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    response = requests.post(
        url,
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Bot Alertas <mailgun@{MAILGUN_DOMAIN}>",
            "to": EMAIL_DESTINO,
            "subject": subject,
            "text": body
        }
    )
    if response.status_code != 200:
        print("❌ Erro ao enviar e-mail:", response.text)
    else:
        print("📧 E-mail enviado com sucesso!")


# Cliente do Telegram
client = TelegramClient(StringSession(session_string), api_id, api_hash)


@client.on(events.NewMessage(chats=canais_monitorados))
async def handler(event):
    texto = event.raw_text
    canal = event.chat.title or event.chat.username
    if any(p.lower() in texto.lower() for p in palavras_chave):
        print(f"🔔 Palavra-chave detectada no canal {canal}: {texto}")
        enviar_email(
            subject=f"🔔 Alerta do Telegram - {canal}",
            body=texto
        )


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        await client.start()
        enviar_email(
            subject="🤖 Bot Iniciado",
            body="O bot de alertas está rodando!"
        )
        print("🤖 Bot iniciado...")
        await client.run_until_disconnected()

    loop.run_until_complete(runner())



# Web server para manter online no Render
app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot está rodando!"


threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
