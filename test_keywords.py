"""
Script de teste para validar o monitoramento de palavras-chave e envio de emails
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Carregar variáveis de ambiente
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Palavras-chave e canais monitorados (igual ao main.py)
PALAVRAS_CHAVE = ["qned70", "nimbus 28", "cumulus 28", "UA7500"]
CANAIS_MONITORADOS = ["vrlofertas", "ofertasepromoaquibr", "canaldeofertasecupons", "TudoPromo", "eieutil_MercadoLi", "bugsepromos", "ctofertascelulares", "teniscertocupons"]

# Credenciais Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY") or os.getenv("MAILGUN_KEY") or ""
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN") or os.getenv("MAILGUN_ZONE") or ""
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO") or os.getenv("MAILGUN_TO") or ""

def enviar_email(subject, body):
    """Envia email via Mailgun API"""
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN or not EMAIL_DESTINO:
        print("⚠️ E-mail não pode ser enviado: as variáveis Mailgun não estão configuradas.")
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
            print("✅ E-mail enviado com sucesso!")
            return True

        print(f"❌ Erro ao enviar e-mail: {response.status_code} - {response.text}")
        return False
    except requests.RequestException as exc:
        print(f"❌ Exceção ao enviar e-mail: {exc}")
        return False

def simular_mensagem(canal, texto):
    """Simula a recepção de uma mensagem de um canal"""
    print(f"\n📨 Simulando mensagem do canal '{canal}':")
    print(f"   Texto: {texto}")
    
    # Verifica se alguma palavra-chave está presente
    palavras_detectadas = [p for p in PALAVRAS_CHAVE if p.lower() in texto.lower()]
    
    if palavras_detectadas:
        print(f"✓ Palavra(s)-chave detectada(s): {', '.join(palavras_detectadas)}")
        enviar_email(
            subject=f"🔔 Alerta do Telegram - {canal}",
            body=f"Canal: {canal}\nMensagem: {texto}"
        )
        return True
    else:
        print(f"✗ Nenhuma palavra-chave detectada")
        return False

def main():
    print("=" * 60)
    print("🧪 TESTE DE PALAVRAS-CHAVE E ENVIO DE EMAIL")
    print("=" * 60)
    
    print(f"\n📋 Configurações:")
    print(f"   Palavras-chave: {PALAVRAS_CHAVE}")
    print(f"   Canais monitorados: {CANAIS_MONITORADOS}")
    print(f"   Email destino: {EMAIL_DESTINO}")
    
    print("\n" + "=" * 60)
    print("🧬 SIMULANDO MENSAGENS")
    print("=" * 60)
    
    # Teste 1: Mensagem com palavra-chave válida
    simular_mensagem("vrlofertas", "PROMOÇÃO: QNED70 com 50% de desconto! Não perca!")
    
    # Teste 2: Mensagem com outra palavra-chave
    simular_mensagem("ofertasepromoaquibr", "Chegou o NIMBUS 28 novo na loja!")
    
    # Teste 3: Mensagem SEM palavra-chave (não deve enviar email)
    simular_mensagem("TudoPromo", "Essa é uma mensagem normal sem oferta especial")
    
    # Teste 4: Mensagem com múltiplas palavras-chave
    simular_mensagem("eieutil_MercadoLi", "CUMULUS 28 e UA7500 com frete grátis por tempo limitado!")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    main()
