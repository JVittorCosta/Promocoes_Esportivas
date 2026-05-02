import imaplib
import email
from email.header import decode_header
import sqlite3
import hashlib
import os
from datetime import datetime

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")

PALAVRAS_CASSINO = [
    "slot", "slots", "cassino", "casino", "roleta", "blackjack",
    "poker", "baccarat", "crash", "mines", "aviator", "fortune",
    "pragmatic", "pgsoft", "spribe", "evolution", "giros",
    "rodadas gratis", "rodadas grátis", "giro gratis", "giro grátis",
    "tigre", "gates", "sugar rush", "sweet bonanza", "big bass",
    "wild", "scatter", "book of", "fortune rabbit", "fortune snake",
    "fortune tiger", "superspin", "supercoins", "golden chips",
    "playtech", "evoplay", "popok", "raspadinha",
]

PALAVRAS_PROMO_VALIDAS = [
    "aposta gratis", "aposta grátis", "freebet", "free bet",
    "cashback futebol", "cashback esport", "cashback na champions",
    "cashback na libertadores", "cashback no brasileirao",
    "cashback da liberta", "empate premiado",
    "super odds", "superodds", "odds aumentadas", "golden boost",
    "super aposta turbinada", "turbinada", "super aumentada",
    "mega impulso", "ou anula", "marca ou anula",
    "ganhe r$", "ganhe ate r$", "aposte r$",
    "aposta sem risco", "reembolso",
    "bonus futebol", "bonus esport", "bonus apostas",
    "missao", "missão", "desafio",
    "utilize a ferramenta criar aposta",
    "garanta 100%", "garanta 50%",
    "50% cashback", "25% cashback", "20% cashback",
    "100% do valor", "chance extra",
    "em apostas gratis", "em freebet", "em creditos",
    "nba playoffs", "kings league",
    "champions league e ganhe", "libertadores e ganhe",
    "brasileirao e ganhe",
]

DOMINIOS_APOSTAS = [
    "bet365", "betsson", "betano", "sportingbet", "superbet",
    "betsul", "kto", "galerabet", "galera", "hiperbet", "hiper",
    "f12bet", "f12", "estrelabet", "estrela", "vaidebet",
    "meridianbet", "meridian", "multibet", "vivasorte", "viva",
    "reidopitaco", "lottu", "sporty", "mcgames", "betesporte",
    "vbet", "bolsadeaposta", "versus", "bandbet", "casadeapostas",
    "betvip", "playbet", "esportesdasorte", "rivalo", "novibet",
    "pixbet", "betnacional", "betwarrior", "bet.br",
]

# Pastas para monitorar — inclui a pasta Apostas criada no Gmail
PASTAS_GMAIL = [
    "Apostas",           # pasta específica que criamos
    "INBOX",             # caixa de entrada
    "[Gmail]/Spam",      # spam
    "[Gmail]/All Mail",  # todos os emails
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

def decodificar_assunto(assunto):
    try:
        partes = decode_header(assunto)
        resultado = ""
        for parte, encoding in partes:
            if isinstance(parte, bytes):
                resultado += parte.decode(encoding or "utf-8", errors="ignore")
            else:
                resultado += parte
        return resultado
    except:
        return str(assunto)

def detectar_tipo(texto):
    t = texto.lower()
    if any(p in t for p in ["aposta gratis", "aposta grátis", "freebet", "free bet", "aposta sem risco", "chance extra", "em apostas gratis", "em freebet"]):
        return "aposta_gratis"
    if any(p in t for p in ["cashback", "empate premiado", "reembolso"]):
        return "cashback"
    if any(p in t for p in ["super odds", "odds aumentadas", "golden boost", "turbinada", "mega impulso", "ou anula", "superodds"]):
        return "super_odds"
    if any(p in t for p in ["missao", "missão", "desafio"]):
        return "missao"
    if any(p in t for p in ["bonus", "bônus"]):
        return "bonus"
    return "outro"

def identificar_casa(remetente):
    r = remetente.lower()
    mapeamento = {
        "bet365": "Bet365",
        "betsson": "Betsson",
        "betano": "Betano",
        "sportingbet": "Sportingbet",
        "superbet": "Superbet",
        "betsul": "Betsul",
        "kto": "KTO",
        "galerabet": "Galera Bet",
        "galera": "Galera Bet",
        "hiperbet": "Hiper Bet",
        "hiper": "Hiper Bet",
        "f12bet": "F12 Bet",
        "f12": "F12 Bet",
        "estrelabet": "Estrela Bet",
        "estrela": "Estrela Bet",
        "vaidebet": "Vai de Bet",
        "meridianbet": "Meridian Bet",
        "meridian": "Meridian Bet",
        "multibet": "Multi Bet",
        "vivasorte": "Viva Sorte",
        "reidopitaco": "Rei do Pitaco",
        "lottu": "Lottu",
        "sporty": "Sporty",
        "mcgames": "MC Games",
        "betesporte": "Bet Esporte",
        "vbet": "Vbet",
        "bolsadeaposta": "Bolsa de Aposta",
        "versus": "Versus",
        "bandbet": "Band Bet",
        "casadeapostas": "Casa de Apostas",
        "betvip": "Bet VIP",
        "playbet": "Play Bet",
        "esportesdasorte": "Esportes da Sorte",
        "rivalo": "Rivalo",
        "novibet": "Novibet",
        "pixbet": "Pix Bet",
        "betnacional": "Bet Nacional",
    }
    for chave, nome in mapeamento.items():
        if chave in r:
            return nome
    return "Casa de Apostas"

def is_email_valido(remetente, assunto):
    if not any(d in remetente.lower() for d in DOMINIOS_APOSTAS):
        return False
    texto = assunto.lower()
    for cassino in PALAVRAS_CASSINO:
        if cassino in texto:
            return False
    if any(p in texto for p in PALAVRAS_PROMO_VALIDAS):
        return True
    return False

def buscar_emails_pasta(mail, pasta):
    emails = []
    try:
        status, _ = mail.select(f'"{pasta}"')
        if status != "OK":
            print(f"  Pasta {pasta} nao encontrada")
            return []
        _, ids = mail.search(None, "UNSEEN")
        ids_lista = ids[0].split()
        print(f"  Pasta {pasta}: {len(ids_lista)} emails nao lidos")
        for eid in ids_lista[-50:]:
            _, data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            remetente = msg.get("From", "")
            assunto = decodificar_assunto(msg.get("Subject", ""))
            emails.append({
                "id": eid,
                "remetente": remetente,
                "assunto": assunto,
                "pasta": pasta,
            })
    except Exception as e:
        print(f"  Erro pasta {pasta}: {e}")
    return emails

def main():
    if not GMAIL_USER or not GMAIL_PASS:
        print("Credenciais Gmail nao configuradas, pulando email")
        return

    con = init_db()

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        print("Conectado ao Gmail com sucesso")
    except Exception as e:
        print(f"Erro ao conectar Gmail: {e}")
        return

    todos_emails = []
    ids_vistos = set()

    for pasta in PASTAS_GMAIL:
        emails = buscar_emails_pasta(mail, pasta)
        for em in emails:
            chave = f"{em['remetente']}_{em['assunto']}"
            if chave not in ids_vistos:
                ids_vistos.add(chave)
                todos_emails.append(em)

    mail.logout()

    print(f"\nTotal: {len(todos_emails)} emails unicos encontrados")

    novas = 0
    for em in todos_emails:
        remetente = em["remetente"]
        assunto = em["assunto"]

        if not is_email_valido(remetente, assunto):
            continue

        casa = identificar_casa(remetente)
        uid = hashlib.md5(f"email_{remetente}_{assunto}".encode()).hexdigest()

        try:
            con.execute(
                "INSERT INTO promocoes VALUES (?,?,?,?,?,?,?,0)",
                (uid, f"{casa} (Email)", assunto, "",
                 "", detectar_tipo(assunto),
                 datetime.now().isoformat())
            )
            con.commit()
            novas += 1
            print(f"Nova: {assunto[:60]}")
        except:
            pass

    print(f"{novas} promocoes novas encontradas no email")

if __name__ == "__main__":
    main()
