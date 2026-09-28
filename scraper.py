#!/usr/bin/env python3
"""
Scraper + generatore feed RSS non ufficiale per le News/Eventi
dell'Ecomuseo di Mantova (https://www.ecomuseomantova.it/news-eventi/pagina-1)

Il sito non offre un feed RSS ufficiale: questo script fa scraping della
pagina elenco (solo pagina-1, cioè le news più recenti) e genera un feed
RSS 2.0 valido, pubblicato poi su GitHub Pages.

Ogni news nella pagina è marcata da un blocco `div.col4` (immagine) seguito
da `div.col444 > div.blk-txt` con data, eventuale luogo, titolo/link e
descrizione. La data mostrata è la data dell'evento/news (formato gg.mm.aaaa),
non un timestamp di pubblicazione: viene usata come pubDate del feed.
"""

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.ecomuseomantova.it"
LIST_URL = f"{BASE_URL}/news-eventi/pagina-1"

FEED_PATH = os.path.join(os.path.dirname(__file__), "docs", "feed.xml")
MAX_ITEMS = 50

HEADERS = {
    # Simula un accesso da browser Firefox 156 su Windows, per ridurre
    # il rischio di blocchi anti-bot
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:156.0) "
        "Gecko/20100101 Firefox/156.0"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
}


def fetch_list_page():
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_items(html):
    """
    Estrae la lista di news/eventi dalla pagina elenco.

    Ritorna una lista di dict: {title, link, description, pub_date_raw, guid}

    Ogni news è racchiusa in <div class="col444"><div class="blk-txt">...
    con dentro:
      - <h5> con la data "gg.mm.aaaa" e, opzionalmente, un link al luogo
        (<a href="news-eventi/filtra/...">)
      - <h3><a href="news-eventi/<id>/<slug>">Titolo</a></h3>
      - <p>descrizione breve</p> (spesso vuoto)
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for block in soup.select("div.col444 > div.blk-txt"):
        h3_link = block.select_one("h3 a[href]")
        if not h3_link:
            continue
        href = h3_link.get("href", "").strip()
        if not href:
            continue
        link = href if href.startswith("http") else f"{BASE_URL}/{href.lstrip('/')}"

        title = h3_link.get_text(strip=True)
        if not title:
            continue

        p_tag = block.select_one("p")
        description = p_tag.get_text(strip=True) if p_tag else ""

        h5 = block.select_one("h5")
        pub_date_raw = None
        if h5:
            h5_text = h5.get_text(" ", strip=True)
            date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", h5_text)
            if date_match:
                pub_date_raw = date_match.group(0)

            location_tag = h5.select_one("a[href*='news-eventi/filtra/']")
            if location_tag:
                location = location_tag.get_text(strip=True)
                description = f"{description} — {location}" if description else location

        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "pub_date_raw": pub_date_raw,
                "guid": hashlib.sha256(link.encode("utf-8")).hexdigest(),
            }
        )

    return items[:MAX_ITEMS]


def parse_pub_date(raw):
    """Interpreta la data mostrata sul sito (formato gg.mm.aaaa); se assente/non
    interpretabile, usa il momento corrente (UTC)."""
    if raw:
        for fmt in ("%d.%m.%Y", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(raw, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    return datetime.now(timezone.utc)


def build_feed(items):
    fg = FeedGenerator()
    fg.id(LIST_URL)
    fg.title("Ecomuseo di Mantova — News ed Eventi (feed non ufficiale)")
    fg.link(href=LIST_URL, rel="alternate")
    fg.description(
        "Feed RSS non ufficiale delle news e degli eventi pubblicati da "
        "Ecomuseo di Mantova (ecomuseomantova.it)."
    )
    fg.language("it")

    for item in items:
        fe = fg.add_entry()
        fe.id(item["link"])
        fe.title(item["title"])
        fe.link(href=item["link"])
        fe.description(item["description"])
        fe.guid(item["guid"], permalink=False)
        fe.pubDate(format_datetime(parse_pub_date(item["pub_date_raw"])))

    return fg


def read_existing_feed():
    if os.path.exists(FEED_PATH):
        with open(FEED_PATH, "rb") as f:
            return f.read()
    return None


def main():
    html = fetch_list_page()
    items = parse_items(html)

    if not items:
        # Diagnostica: se il sito cambia markup o restituisce una pagina di
        # blocco anti-bot, salviamo l'HTML ricevuto per poterlo ispezionare
        # dai log della GitHub Action, invece di fallire "in silenzio".
        debug_path = os.path.join(os.path.dirname(__file__), "debug_last_response.html")
        try:
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Nessun elemento trovato. HTML salvato in {debug_path} per debug.", file=sys.stderr)
        except OSError:
            print("Nessun elemento trovato (impossibile salvare HTML di debug).", file=sys.stderr)
        sys.exit(1)

    fg = build_feed(items)
    new_feed_bytes = fg.rss_str(pretty=True)

    existing = read_existing_feed()
    if existing == new_feed_bytes:
        print("Feed invariato, nessun commit necessario.")
        return

    os.makedirs(os.path.dirname(FEED_PATH), exist_ok=True)
    with open(FEED_PATH, "wb") as f:
        f.write(new_feed_bytes)
    print(f"Feed aggiornato con {len(items)} elementi.")


if __name__ == "__main__":
    main()
