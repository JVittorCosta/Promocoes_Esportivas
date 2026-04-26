import asyncio
from playwright.async_api import async_playwright
import sqlite3
import hashlib
from datetime import datetime

CASAS = [
    {"nome": "Bet365", "url": "https://www.bet365.bet.br/#/HO/"},
    {"nome": "Lottu", "url": "https://www.lottu.bet.br/sports"},
    {"nome": "Sporty", "url": "https://www.sporty.bet.br/br/"},
    {"nome": "Betsson", "url": "https://www.betsson.bet.br/promocoes"},
    {"nome": "Esportes da Sorte", "url": "https://esportesdasorte.bet.br/ptb/bet/main"},
    {"nome": "Jogo de Ouro", "url": "https://jogodeouro.bet.br/pt/sports#/overview"},
    {"nome": "Superbet", "url": "https://superbet.bet.br/"},
    {"nome": "Esportiva", "url": "https://esportiva.bet.br/sports"},
    {"nome": "Betsul", "url": "https://betsul.bet.br/"},
    {"nome": "MCGames", "url": "https://mcgames.bet.br/sports"},
    {"nome": "Betwarrior", "url": "https://apostas.betwarrior.bet.br/pt-br/sports/home"},
    {"nome": "Galera Bet", "url": "https://www.galera.bet.br/"},
    {"nome": "KTO", "url": "https://www.kto.bet.br/"},
    {"nome": "Pix Bet", "url": "https://pix.bet.br/sports/"},
    {"nome": "Bet Nacional", "url": "https://betnacional.bet.br/"},
    {"nome": "F12 Bet", "url": "https://f12.bet.br/prejogo/"},
    {"nome": "Lottoland", "url": "https://www.lottoland.bet.br/ofertas#esportes"},
    {"nome": "Sorteo Online", "url": "https://www.sorteonline.bet.br/ofertas#Aposta-Esportiva"},
    {"nome": "BetMGM", "url": "https://www.betmgm.bet.br/aposta-esportiva#featured"},
    {"nome": "Bet Esporte", "url": "https://betesporte.bet.br/sports/desktop"},
    {"nome": "Vbet", "url": "https://www.vbet.bet.br/pb/promotions/sport"},
    {"nome": "Betfair", "url": "https://www.betfair.bet.br/apostas/"},
    {"nome": "Viva Sorte", "url": "https://vivasorte.bet.br/apostas-esportivas/destaques"},
    {"nome": "Versus", "url": "https://www.versus.bet.br/esportes"},
    {"nome": "Rivalo", "url": "https://www.rivalo.bet.br/pt/promotions"},
    {"nome": "Vupi", "url": "https://www.vupi.bet.br/"},
    {"nome": "Rei do Pitaco", "url": "https://reidopitaco.bet.br/promocoes"},
    {"nome": "Betpix365", "url": "https://betpix365.bet.br/ptb/bet/main"},
    {"nome": "Vai de Bet", "url": "https://vaidebet.bet.br/ptb/bet/main"},
    {"nome": "7K Bet", "url": "https://7k.bet.br/sports"},
    {"nome": "Cassino Bet", "url": "https://cassino.bet.br/sports"},
    {"nome": "Vera Bet", "url": "https://vera.bet.br/sports"},
    {"nome": "Bateu Bet", "url": "https://bateu.bet.br/sports"},
    {"nome": "Seu Bet", "url": "https://www.seu.bet.br/pre-jogo/match/topLeague"},
    {"nome": "Faz1 Bet", "url": "https://faz1.bet.br/br"},
    {"nome": "Betfast", "url": "https://betfast.bet.br/br/"},
    {"nome": "Bet da Sorte", "url": "https://betdasorte.bet.br/sports"},
    {"nome": "Betao", "url": "https://betao.bet.br"},
    {"nome": "Casa de Apostas", "url": "https://casadeapostas.bet.br/br/sports"},
    {"nome": "Brasil da Sorte", "url": "https://www.brasildasorte.bet.br/sports#/overview"},
    {"nome": "Seguro Bet", "url": "https://www.seguro.bet.br/"},
    {"nome": "BR4 Bet", "url": "https://br4.bet.br/sports#/overview"},
    {"nome": "Lotogreen", "url": "https://lotogreen.bet.br/sports#/overview"},
    {"nome": "Golde Bet", "url": "https://goldebet.bet.br/sports#/overview"},
    {"nome": "Alfa Bet", "url": "https://alfa.bet.br/"},
    {"nome": "Luva Bet", "url": "https://luva.bet.br/promotions"},
    {"nome": "Hiper Bet", "url": "https://hiper.bet.br/ptb/bet/main"},
    {"nome": "Estrela Bet", "url": "https://www.estrelabet.bet.br/pb/esportes"},
    {"nome": "Aposta Ganha", "url": "https://www.apostaganha.bet.br/"},
    {"nome": "Stake", "url": "https://stake.bet.br/esportes/"},
    {"nome": "Pagol", "url": "https://pagol.bet.br/br/aposta-esportiva"},
    {"nome": "4Play Bet", "url": "https://4play.bet.br/apostas-esportivas/destaques"},
    {"nome": "Bet VIP", "url": "https://betvip.bet.br/sports"},
    {"nome": "Ganhei Bet", "url": "https://ganhei.bet.br/sports"},
    {"nome": "Play Bet", "url": "https://play.bet.br/"},
    {"nome": "Maxima Bet", "url": "https://maxima.bet.br/pb/promotions/all"},
    {"nome": "Betaki", "url": "https://betaki.bet.br/profile/promo"},
    {"nome": "Up Bet", "url": "https://up.bet.br/pt-BR/sports/live#/overview"},
    {"nome": "Start Bet", "url": "https://start.bet.br/promotions"},
    {"nome": "Band Bet", "url": "https://www.bandbet.bet.br/apostas-esportivas/ao-vivo"},
    {"nome": "BRX Bet", "url": "https://brx.bet.br/sports?tab=Early"},
    {"nome": "Bulls Bet", "url": "https://bullsbet.bet.br/sports?eventlistTab=Early"},
    {"nome": "Lance de Sorte", "url": "https://lancedesorte.bet.br/sports/desktop"},
    {"nome": "Apostou", "url": "https://www.apostou.bet.br/home/events-area"},
    {"nome": "Bravo Bet", "url": "https://www.bravo.bet.br/"},
    {"nome": "BR Bet", "url": "https://www.brbet.bet.br/home/events-area"},
    {"nome": "MMA Bet", "url": "https://mmabet.bet.br/sports/"},
    {"nome": "Multi Bet", "url": "https://multi.bet.br/sports#/overview"},
]

KEYWORDS = {
    "aposta_gratis": ["aposta gratis", "aposta grátis", "free bet", "freebet", "aposta sem risco"],
    "cashback": ["cashback", "cash back", "dinheiro de volta"],
    "super_odds": ["super odds", "odds aumentadas", "odds turbinadas", "odds melhoradas", "boost"],
    "bonus": ["bonus", "bônus", "boas-vindas", "primeiro deposito", "primeiro depósito"],
}

PALAVRAS_PROMO = [
    "gratis", "grátis", "freebet", "cashback", "bonus", "bônus",
    "odds", "boost", "deposito", "depósito", "oferta", "promoção",
    "promocao", "reembolso", "free", "ganhe", "ganha", "aposta gratis",
    "aposta grátis", "sem risco", "dobro", "multiplica"
]

PALAVRAS_CASSINO = [
    "cassino", "casino", "slot", "slots", "roleta", "blackjack",
    "poker", "pôquer", "baccarat", "caça-niquel", "jackpot",
    "crash", "mines", "aviator", "fortune", "pragmatic", "pgsoft",
    "spribe", "evolution", "bacbo", "dragon tiger"
]

PALAVRAS_ESPORTE = [
    "futebol", "basquete", "tenis", "tênis", "vôlei", "volei",
    "esporte", "sport", "jogo", "partida", "campeonato", "liga",
    "aposta esportiva", "pre-jogo", "ao vivo", "handicap"
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

def detectar_tipo(titulo, descricao):
    texto = (titulo + " " + descricao).lower()
    for tipo, palavras in KEYWORDS.items():
        if any(p in texto for p in palavras):
            return tipo
    return "outro"

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
    try:
        page = await browser.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        await page.goto(casa["url"], timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        elementos = await page.query_selector_all(
            "[class*='promo'], [class*='bonus'], [class*='offer'], [class*='banner'], "
            "[class*='promotion'], [class*='campanha'], [class*='destaque'], "
            "[class*='sport'], [class*='esport']"
        )

        promos = []
        vistos = set()

        for el in elementos[:30]:
            titulo = (await el.inner_text()).strip()[:200]
            titulo = titulo.split("\n")[0].strip()

            if len(titulo) < 10 or titulo in vistos:
                continue

            titulo_lower = titulo.lower()

            if not any(p in titulo_lower for p in PALAVRAS_PROMO):
                continue

            if any(p in titulo_lower for p in PALAVRAS_CASSINO):
                continue

            vistos.add(titulo)

            uid = hashlib.md5(f"{casa['nome']}{titulo}".encode()).hexdigest()
            promos.append({
                "id": uid,
                "casa": casa["nome"],
                "titulo": titulo,
                "descricao": "",
                "url": casa["url"],
                "tipo": detectar_tipo(titulo, ""),
                "data_coleta": datetime.now().isoformat(),
            })

        await page.close()
        print(f"{casa['nome']}: {len(promos)} promocoes esportivas encontradas")
        return promos

    except Exception as e:
        print(f"Erro em {casa['nome']}: {e}")
        try:
            await page.close()
        except:
            pass
        return []

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
