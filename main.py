from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import os
import sys
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio

load_dotenv()

# 🔑 Credenciais do Telegram
api_id = int(os.getenv("API_ID") or 0)
api_hash = os.getenv("API_HASH") or ""
session_string = os.getenv("SESSION_STRING") or ""
bot_token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or ""

# 📧 Credenciais Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY") or os.getenv("MAILGUN_API_KEY") or os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN") or os.getenv("MAILGUN_DOMAIN")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO") or os.getenv("EMAIL_DESTINO")

if not api_id or not api_hash:
    raise RuntimeError("API_ID e API_HASH devem ser configurados nas variáveis de ambiente.")

if not session_string and not bot_token:
    raise RuntimeError("Defina SESSION_STRING ou BOT_TOKEN para autenticar o cliente Telegram.")

# 📢 Configuração de canais e palavras-chave
palavras_chave = ["qned70", "nimbus 28", "cumulus 28", "UA7500"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares", "teniscertocupons"]

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
        if bot_token:
            await client.start(bot_token=bot_token)
        else:
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


if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
