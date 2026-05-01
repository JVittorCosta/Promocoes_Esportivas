import asyncio
from playwright.async_api import async_playwright
import sqlite3
import hashlib
from datetime import datetime

CASAS = [
    {"nome": "Bet365", "url": "https://www.bet365.bet.br/#/HO/"},
    {"nome": "Lottu", "url": "https://www.lottu.bet.br/sports"},
    {"nome": "Sporty", "url": "https://www.sporty.bet.br/br/promotions/"},
    {"nome": "Betsson", "url": "https://www.betsson.bet.br/promocoes?filter=sportsbook"},
    {"nome": "Esportes da Sorte", "url": "https://esportesdasorte.bet.br/ptb/bet/main"},
    {"nome": "Betsul", "url": "https://betsul.bet.br/beneficios"},
    {"nome": "MCGames", "url": "https://mcgames.bet.br/sports"},
    {"nome": "Betano", "url": "https://www.betano.bet.br/"},
    {"nome": "Sportingbet", "url": "https://www.sportingbet.bet.br/pt-br/promo/offers/p/sportsbook"},
    {"nome": "KTO", "url": "https://www.kto.bet.br/promo/sports"},
    {"nome": "F12 Bet", "url": "https://f12.bet.br/prejogo/"},
    {"nome": "Vbet", "url": "https://www.vbet.bet.br/pb/promotions/sport"},
    {"nome": "Bet Esporte", "url": "https://betesporte.bet.br/sports/desktop/promotions"},
    {"nome": "Viva Sorte", "url": "https://vivasorte.bet.br/promocoes"},
    {"nome": "Versus", "url": "https://www.versus.bet.br/promos"},
    {"nome": "Rei do Pitaco", "url": "https://reidopitaco.bet.br/promocoes?tab=all"},
    {"nome": "Meridian Bet", "url": "https://meridianbet.bet.br/promo/ca/category/1413"},
    {"nome": "7K Bet", "url": "https://7k.bet.br/promotions"},
    {"nome": "Vera Bet", "url": "https://vera.bet.br/promotions"},
    {"nome": "Superbet", "url": "https://superbet.bet.br/promocoes-e-bonus"},
    {"nome": "Casa de Apostas", "url": "https://casadeapostas.bet.br/br/promo"},
    {"nome": "Hiper Bet", "url": "https://hiper.bet.br/ptb/contents/promotions"},
    {"nome": "Multi Bet", "url": "https://multi.bet.br/pb/promotions/sports"},
    {"nome": "Bet VIP", "url": "https://betvip.bet.br/promotions"},
    {"nome": "Play Bet", "url": "https://play.bet.br/sports"},
    {"nome": "Band Bet", "url": "https://www.bandbet.bet.br/promocoes"},
    {"nome": "Bolsa de Aposta", "url": "https://bolsadeaposta.bet.br/b/exchange/custom-markets"},
]

TITULOS_GENERICOS = [
    "multiplas turbinadas", "odds turbinadas", "super odds",
    "odds aumentadas", "freebet", "free bet", "cashback",
    "bonus", "bônus", "promocoes", "promoções", "destaques",
    "esportes", "ver todos", "participar", "saiba mais",
    "ler mais", "todas", "ambos", "copa libertadores",
    "champions league", "brasileirao", "premier league",
    "encerra em", "tempo restante", "quiz", "bolao",
    "como usar", "indique e ganhe", "1 ano", "mega bonus",
]

PALAVRAS_CASSINO = [
    "cassino", "casino", "slot", "slots", "roleta", "blackjack",
    "poker", "pôquer", "baccarat", "jackpot", "crash", "mines",
    "aviator", "fortune", "pragmatic", "pgsoft", "spribe",
    "evolution", "bacbo", "dragon tiger", "giros", "giro gratis",
    "giro grátis", "rodadas gratis", "rodadas grátis", "tigre",
    "gates", "sugar rush", "sweet bonanza", "big bass", "wild",
    "scatter", "fruit", "book of", "diamond", "bonus buy",
    "hold and win", "sortudo", "raspadinha", "popok", "evoplay",
    "aviatrix", "fortune rabbit", "fortune snake", "fortune tiger",
    "fortune ox", "rico gorila", "jaguar dojo", "rico rabbit",
    "rico dj", "yo dragon", "torneio evoplay", "superspin",
    "supercoins", "popok gaming", "playtech", "golden chips",
    "live casino", "mega bonus playtech", "playtech live",
]

PALAVRAS_LIXO = [
    "cookie", "privacidade", "você concorda", "política de privacidade",
    "é seguro apostar", "não é permitido apostar com recursos",
    "decimal", "americanas", "hongkong", "formato de odds",
    "minha conta", "notificacoes", "chat social", "depositar",
    "retirada", "historico", "detalhes da conta", "verificacao",
    "jogo responsavel", "configuracoes", "ajuda", "suporte",
    "unable to access", "sorry", "você foi bloqueado", "blocked",
    "onde assistir", "horario e odds", "ao vivo:",
    "1º tempo", "2º tempo", "ganhador", "empate", "suspenso",
    "esportes ativos", "clique aqui e confira",
    "ver todos", "participe", "participar", "saiba mais",
    "ler mais", "ver detalhes", "concorra a ate",
    "golden chips", "mega bonus",
]

PALAVRAS_PROMO_VALIDAS = [
    "ganhe ate r$", "ganhe r$", "aposte r$", "ate r$",
    "aposta gratis", "aposta grátis", "freebet", "free bet",
    "aposta sem risco", "reembolso", "bet & get",
    "cashback futebol", "cashback esport", "cashback na champions",
    "cashback na libertadores", "cashback no brasileirao",
    "super aposta turbinada", "turbinada da play",
    "mega impulso", "ou anula", "superodds",
    "odds aumentadas de hoje", "multiplas turbinadas em ate",
    "bonus acumulador", "acumulador turbinado",
    "combo boost", "comboboost", "quiz brasileirao",
    "bolao europeu", "liga da galera",
    "kings league", "aposte e ganhe na champions",
    "utilize a ferramenta criar aposta",
    "garanta 100%", "garanta 50%",
    "50% cashback", "25% cashback", "20% cashback",
    "100% do valor", "dobro da odd",
    "garanta sua freebet", "desafio das odds",
    "palpite na champions", "palpite na liberta",
    "quem sabe faz ao vivo", "liga da galera",
    "golden boost", "super aumentada", "marca ou anula",
    "empate premiado", "missao criar aposta",
    "aposte no brasileirao", "aposte nos torneios",
    "chance extra", "nba playoffs",
    "em apostas gratis", "em freebet", "em creditos",
]

PALAVRAS_ESPECIAIS = {
    "Lottu": ["super aposta turbinada"],
    "Esportes da Sorte": ["super aposta turbinada"],
    "Bet VIP": ["odds aumentadas"],
    "Play Bet": ["turbinada da play"],
    "Bolsa de Aposta": ["ou anula", "marca ou anula"],
    "Superbet": ["golden boost"],
    "Meridian Bet": ["freebet todos os dias"],
}

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

def detectar_tipo(titulo, descricao):
    texto = (titulo + " " + descricao).lower()
    if any(p in texto for p in ["aposta gratis", "aposta grátis", "free bet", "freebet", "aposta sem risco", "chance extra", "nba playoffs", "em apostas gratis", "em freebet"]):
        return "aposta_gratis"
    if any(p in texto for p in ["cashback", "empate premiado"]):
        return "cashback"
    if any(p in texto for p in ["super odds", "odds aumentadas", "golden boost", "turbinada", "mega impulso", "ou anula", "superodds", "super aumentada"]):
        return "super_odds"
    if any(p in texto for p in ["missao", "missão", "liga da galera", "quiz", "bolao", "desafio"]):
        return "missao"
    if any(p in texto for p in ["bonus", "bônus"]):
        return "bonus"
    return "outro"

def is_titulo_generico(titulo):
    t = titulo.lower().strip()
    for gen in TITULOS_GENERICOS:
        if t == gen:
            return True
    return False

def is_valido(titulo, casa_nome):
    t = titulo.lower().strip()
    if len(t) < 15 or len(t) > 150:
        return False
    if is_titulo_generico(t):
        return False
    for lixo in PALAVRAS_LIXO:
        if lixo in t:
            return False
    for cassino in PALAVRAS_CASSINO:
        if cassino in t:
            return False
    palavras_especiais = PALAVRAS_ESPECIAIS.get(casa_nome, [])
    if any(p in t for p in palavras_especiais):
        return True
    if any(p in t for p in PALAVRAS_PROMO_VALIDAS):
        return True
    return False

def salvar_novas(con, promos):
    novas = []
    for p in promos:
        try:
            con.execute(
                "INSERT INTO promocoes VALUES (?,?,?,?,?,?,?,0)",
                (p["id"], p["casa"], p["titulo"], p["descricao"],
                 p["url"], p["tipo"], p["data_coleta"])
            )
            novas.append(p)
        except sqlite3.IntegrityError:
            pass
    con.commit()
    return novas

async def scrape_casa(browser, casa):
    page = await browser.new_page()
    try:
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        await page.goto(casa["url"], timeout=25000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        elementos = await page.query_selector_all(
            "h1, h2, h3, h4, "
            "[class*='promo'], [class*='offer'], [class*='banner'], "
            "[class*='promotion'], [class*='boost'], [class*='golden'], "
            "[class*='turbin'], [class*='impulso'], [class*='odds'], "
            "[class*='mission'], [class*='missao'], [class*='cashback']"
        )

        promos = []
        titulos_vistos = set()

        for el in elementos[:50]:
            try:
                titulo = (await el.inner_text()).strip()
                titulo = titulo.split("\n")[0].strip()
            except:
                continue
            if titulo in titulos_vistos:
                continue
            if not is_valido(titulo, casa["nome"]):
                continue
            titulos_vistos.add(titulo)

            desc = ""
            try:
                parent = await el.evaluate_handle(
                    "el => el.closest('article, section, li') || el.parentElement"
                )
                desc = (await parent.as_element().inner_text()).strip()[:300]
            except:
                pass

            uid = hashlib.md5(f"{casa['nome']}{titulo}".encode()).hexdigest()
            promos.append({
                "id": uid,
                "casa": casa["nome"],
                "titulo": titulo,
                "descricao": desc,
                "url": casa["url"],
                "tipo": detectar_tipo(titulo, desc),
                "data_coleta": datetime.now().isoformat(),
            })

        print(f"{casa['nome']}: {len(promos)} promocoes validas")
        return promos

    except Exception as e:
        print(f"Erro em {casa['nome']}: {e}")
        return []
    finally:
        await page.close()

async def main():
    con = init_db()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for casa in CASAS:
            promos = await scrape_casa(browser, casa)
            novas = salvar_novas(con, promos)
            print(f"  -> {len(novas)} novas salvas")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
