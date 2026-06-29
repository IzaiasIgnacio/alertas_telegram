from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient(StringSession(), api_id, api_hash)
client.start()
session_string = client.session.save()
client.disconnect()

if not session_string:
    raise RuntimeError("Não foi possível gerar uma SESSION_STRING válida.")

print(session_string)

env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path, "r", encoding="utf-8") as env_file:
    lines = env_file.readlines()

updated_lines = []
replaced = False
for line in lines:
    if line.startswith("SESSION_STRING="):
        if not replaced:
            updated_lines.append(f"SESSION_STRING={session_string}\n")
            replaced = True
    else:
        updated_lines.append(line)

if not replaced:
    updated_lines.append(f"SESSION_STRING={session_string}\n")

with open(env_path, "w", encoding="utf-8") as env_file:
    env_file.writelines(updated_lines)

print("✅ SESSION_STRING salva no arquivo .env")