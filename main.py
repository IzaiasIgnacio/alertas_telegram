from telethon import TelegramClient, events
from dotenv import load_dotenv
import yagmail
import asyncio
import os

# === CONFIGURAÇÕES ===

load_dotenv()

api_id = 22618574
api_hash = "0cbd969ef0e780bc9ccfbc38bc947d94"
session_name = "izaias_telethon_bot"

palavras_chave = ["q800d", "q800f", "s25"]

# Apenas canais permitidos
# Use usernames sem @ ou IDs numéricos
canais_permitidos = ["vrlofertas","ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares"]

EMAIL_REMETENTE = "izaias.ignacio@gmail.com"
EMAIL_DESTINO = "izaias.ignacio@outlook.com"
SENHA_APP = os.environ.get("EMAIL_APP_PASSWORD")

yag = yagmail.SMTP(EMAIL_REMETENTE, SENHA_APP)

# === CLIENTE TELEGRAM ===

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=None))
async def handler(event):
    try:
        sender = await event.get_chat()
        chat_title = getattr(sender, 'title', 'Desconhecido')
        username = getattr(sender, 'username', None)
        channel_id = sender.id
        msg = event.message.message or "[sem texto]"

        # Verifica se o canal está na lista permitida
        canal_id_str = str(channel_id)
        if username not in canais_permitidos and canal_id_str not in canais_permitidos:
            return  # Ignora mensagens de canais não permitidos

        print("\n📨 Nova mensagem recebida:")
        print(f"🧾 Canal: {chat_title}")
        print(f"👤 Username: {username}")
        print(f"📄 Conteúdo: {msg}")

        # Verifica palavras-chave
        if any(p.lower() in msg.lower() for p in palavras_chave):
            print("🚨 Palavra-chave detectada! Enviando e-mail...")

            yag.send(
                to=EMAIL_DESTINO,
                subject="🚨 Palavra-chave encontrada no Telegram",
                contents=f"📌 Canal: {chat_title}\n🔗 Username: @{username}\n\n📄 Mensagem:\n{msg}"
            )
            print("✅ E-mail enviado com sucesso.")

    except Exception as e:
        print(f"⚠️ Erro no handler: {e}")

async def main():
    print("🤖 Iniciando Telethon com filtro de canal...")
    await client.start()
    print("🔍 Aguardando mensagens nos canais permitidos...")
    await client.run_until_disconnected()

asyncio.run(main())
