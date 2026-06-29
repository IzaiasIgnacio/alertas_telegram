from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import os
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# 🔑 Credenciais do Telegram
raw_test_mode = os.getenv("TEST_MODE", "")
RUN_BOT = os.getenv("RUN_BOT", "0").lower() in {"1", "true", "yes", "on"}
TEST_MODE = raw_test_mode.lower() in {"1", "true", "yes", "on"} if raw_test_mode else not RUN_BOT
api_id = int(os.getenv("API_ID") or 0)
api_hash = os.getenv("API_HASH") or ""
session_string = os.getenv("SESSION_STRING") or ""
bot_token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or ""
has_telegram_credentials = bool(api_id and api_hash and (session_string or bot_token))

if RUN_BOT and not has_telegram_credentials:
    raise RuntimeError("RUN_BOT=1 exige API_ID, API_HASH e SESSION_STRING ou BOT_TOKEN.")

if TEST_MODE:
    print("🧪 Modo de teste ativo: o bot não tentará fazer login interativo no Telegram.")

# 📧 Credenciais Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY") or os.getenv("MAILGUN_KEY") or ""
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN") or os.getenv("MAILGUN_ZONE") or ""
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO") or os.getenv("MAILGUN_TO") or ""

if TEST_MODE:
    print("🧪 Modo de teste ativo: pulando o login do Telegram para validar e-mail e Flask.")

# 📢 Configuração de canais e palavras-chave
palavras_chave = ["qned70", "nimbus 28", "cumulus 28", "UA7500"]
canais_monitorados = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares", "teniscertocupons"]

# Função de envio via Mailgun API
def enviar_email(subject, body):
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN or not EMAIL_DESTINO:
        print("⚠️ E-mail não enviado: as variáveis Mailgun não estão configuradas.")
        return False

    try:
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        response = requests.post(
            url,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Bot Alertas <mailgun@{MAILGUN_DOMAIN}>",
                "to": EMAIL_DESTINO,
                "subject": subject,
                "text": body
            },
            timeout=15,
        )
        if response.status_code == 200:
            print("📧 E-mail enviado com sucesso!")
            return True

        print(f"❌ Erro ao enviar e-mail: {response.status_code} - {response.text}")
        return False
    except requests.RequestException as exc:
        print(f"❌ Exceção ao enviar e-mail: {exc}")
        return False


# Cliente do Telegram
client = None
if not TEST_MODE:
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
    if TEST_MODE or client is None:
        print("🧪 Modo de teste local ativo: pulando o login do Telegram.")
        enviar_email("🧪 Teste local", "Este e-mail foi enviado pelo modo de teste local.")
        print("🧪 Modo de teste concluído. O Flask continua rodando.")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        try:
            if bot_token:
                await client.start(bot_token=bot_token)
            else:
                await client.start()
        except Exception as exc:
            print(f"⚠️ Falha ao iniciar o cliente Telegram: {exc}")
            return

        threading.Thread(
            target=enviar_email,
            args=("🤖 Bot Iniciado", "O bot de alertas está rodando!"),
            daemon=True,
        ).start()
        print("🤖 Bot iniciado...")
        await client.run_until_disconnected()

    loop.run_until_complete(runner())



# Web server para manter online no Render
app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot está rodando!"

@app.route("/test-email")
def test_email():
    sent = enviar_email("🧪 Teste local", "Teste manual do envio de e-mail.")
    return {"ok": sent}, 200 if sent else 500


if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
