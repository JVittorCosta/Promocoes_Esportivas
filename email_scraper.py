import imaplib
import email
import sqlite3
import hashlib
from datetime import datetime
import os

EMAIL = os.environ.get("OUTLOOK_USER")
SENHA = os.environ.get("OUTLOOK_PASS")

PALAVRAS_PROMO = [
    "gratis", "grátis", "freebet", "cashback", "bonus", "bônus",
    "odds", "boost", "deposito", "depósito", "oferta", "promoção",
    "reembolso", "free bet", "ganhe", "ganha", "aposta gratis",
    "sem risco", "dobro", "multiplica"
]

PALAVRAS_CASSINO = [
    "cassino", "casino", "slot", "slots", "roleta", "blackjack",
    "poker", "baccarat", "jackpot", "crash", "mines", "aviator",
    "giros", "rodadas", "tigre", "wild", "scatter", "spin",
    "sortudo", "caça", "niquel", "raspadinha"
]

CASAS_CONHECIDAS = [
    "bet365", "betsson", "betano", "kto", "rivalo", "galera",
    "estrela", "sportingbet", "betfair", "superbet", "betsul",
    "vaidebet", "f12", "pixbet", "lottu", "sporty", "betnacional",
    "betwarrior", "vivasorte", "versus", "vupi", "reidopitaco",
    "betpix", "cassino", "vera", "bateu", "betfast", "betdasorte",
    "brasildasorte", "lotogreen", "goldebet", "luva", "hiper",
    "apostaganha", "stake", "pagol", "betvip", "ganhei", "maxima",
    "betaki", "start", "bandbet", "brx", "bulls", "lancedesorte",
    "apostou", "bravo", "brbet", "mmabet", "multi"
]

def init_db():
    con = sqlite3.connect("promocoes.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS promocoes (
            id TEXT PRIMARY KEY,
            casa TEXT,
            titulo TEXT,
            descricao TEXT,
            url TEXT,
            tipo TEXT,
            data_coleta TEXT,
            notificado INTEGER DEFAULT 0
        )
    """)
    con.commit()
    return con

def detectar_tipo(texto):
    texto = texto.lower()
    if any(p in texto for p in ["aposta gratis", "aposta grátis", "free bet", "freebet"]):
        return "aposta_gratis"
    if "cashback" in texto:
        return "cashback"
    if any(p in texto for p in ["super odds", "odds aumentadas", "boost"]):
        return "super_odds"
    if any(p in texto for p in ["bonus", "bônus"]):
        return "bonus"
    return "outro"

def buscar_emails():
    con = init_db()
    try:
        mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        mail.login(EMAIL, SENHA)
        mail.select("inbox")

        _, mensagens = mail.search(None, "UNSEEN")
        ids = mensagens[0].split()
        print(f"{len(ids)} emails nao lidos encontrados")

        novas = 0
        for id_ in ids[-50:]:
            _, data = mail.fetch(id_, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            remetente = msg.get("From", "").lower()
            assunto = msg.get("Subject", "")

            if not any(c in remetente for c in CASAS_CONHECIDAS):
                continue

            assunto_lower = assunto.lower()

            if not any(p in assunto_lower for p in PALAVRAS_PROMO):
                continue

            if any(p in assunto_lower for p in PALAVRAS_CASSINO):
                continue

            uid = hashlib.md5(f"email{assunto}{remetente}".encode()).hexdigest()
            casa = next((c for c in CASAS_CONHECIDAS if c in remetente), "casa de aposta")

            try:
                con.execute(
                    "INSERT INTO promocoes VALUES (?,?,?,?,?,?,?,0)",
                    (uid, casa.title(), assunto, "", "", detectar_tipo(assunto), datetime.now().isoformat())
                )
                novas += 1
            except:
                pass

        con.commit()
        print(f"{novas} promocoes novas encontradas no email")

    except Exception as e:
        print(f"Erro ao acessar email: {e}")

if __name__ == "__main__":
    buscar_emails()
