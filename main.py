from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
import yagmail
import os
from dotenv import load_dotenv
from flask import Flask
import threading

# === CONFIG ===
load_dotenv()

api_id = int(os.getenv("api_id"))
api_hash = os.getenv("api_hash")
session_string = os.getenv("session_string")

email_user = os.getenv("email_user")
email_pass = os.getenv("email_app_password")
email_dest = os.getenv("email_dest")

palavras_chave = ["q800d", "q800f", "s25"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares"]

yag = yagmail.SMTP(user=email_user, password=email_pass)

# === FLASK (para manter ativo no Replit) ===
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot rodando!"

def start_flask():
    app_flask.run(host="0.0.0.0", port=8080)

threading.Thread(target=start_flask).start()

# === TELETHON ===
client = TelegramClient(StringSession(session_string), api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    try:
        if event.chat and event.chat.username:
            canal = event.chat.username.lower()
            if canal in [c.lower() for c in canais_monitorados]:
                texto = event.raw_text.lower()
                if any(p in texto for p in palavras_chave):
                    print(f"📢 Palavra-chave encontrada em @{canal}!")
                    yag.send(
                        to=email_dest,
                        subject=f"🚨 Palavra-chave em @{canal}",
                        contents=event.raw_text
                    )
    except Exception as e:
        print(f"Erro no handler: {e}")

print("🤖 Bot iniciando...")
yag.send(
    to=email_dest,
    subject="✅ Bot iniciado",
    contents="O monitor de palavras-chave está ativo."
)

client.start()
client.run_until_disconnected()
