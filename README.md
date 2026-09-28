# ecomuseo_mantova

**Versione: v1.0.0** — vedi [CHANGELOG.md](CHANGELOG.md)

[![Aggiorna feed RSS](https://github.com/mbmichele/ecomuseo_mantova/actions/workflows/update-feed.yml/badge.svg)](https://github.com/mbmichele/ecomuseo_mantova/actions/workflows/update-feed.yml)

Repo: https://github.com/mbmichele/ecomuseo_mantova
Feed pubblicato (dopo aver attivato GitHub Pages): `https://mbmichele.github.io/ecomuseo_mantova/feed.xml`

Feed RSS **non ufficiale** delle news/eventi pubblicati da [Ecomuseo di Mantova](https://www.ecomuseomantova.it/news-eventi/pagina-1), generato tramite scraping (il sito non offre un feed proprio).

## Come funziona

1. `scraper.py` scarica `https://www.ecomuseomantova.it/news-eventi/pagina-1` (simulando un accesso da browser Firefox 156), estrae titolo, link, descrizione/luogo e data di ogni news (dai blocchi `div.col444 > div.blk-txt`) e genera un feed RSS 2.0 in `docs/feed.xml` (max 50 elementi). La data mostrata sul sito è la data dell'evento/news, non un timestamp di pubblicazione, e viene usata come `pubDate` del feed.
2. Il feed viene pubblicato staticamente tramite **GitHub Pages** dalla cartella `/docs` del branch `main`.
3. Una GitHub Action rigenera il feed **ogni ora** e fa commit/push solo se il contenuto è cambiato.
4. Se lo scraping non trova elementi (es. il sito cambia struttura o mostra una pagina anti-bot), l'HTML ricevuto viene salvato come artifact del workflow per il debug, invece di fallire senza spiegazioni.

## Doppio cron: interno + esterno

Come richiesto, l'aggiornamento orario è garantito da due meccanismi indipendenti, entrambi impostati a un'ora:

- **Cron interno di GitHub Actions**: `schedule: cron: "0 * * * *"` nel workflow `.github/workflows/update-feed.yml`. È il meccanismo principale, ma GitHub può ritardarlo nei momenti di carico.
- **Cron esterno** ([cron-job.org](https://cron-job.org), ogni ora): fa da backup/rinforzo chiamando l'API di GitHub per lanciare lo stesso workflow via `workflow_dispatch`, così l'aggiornamento non dipende solo dallo scheduler interno di GitHub.

Poiché i due cron possono scattare quasi in contemporanea, il workflow gestisce l'eventuale conflitto sul push (commit "arrivato prima" dall'altra esecuzione) con **fetch + rebase e retry automatico**, invece di fallire.

Per configurare il cron esterno:

1. Crea un [Personal Access Token](https://github.com/settings/tokens) con permesso `repo` (o un fine-grained token con permesso "Actions: write" su questo repo).
2. Su cron-job.org (o servizio equivalente) crea un job orario che esegue una richiesta:

   ```
   POST https://api.github.com/repos/mbmichele/ecomuseo_mantova/actions/workflows/update-feed.yml/dispatches
   Headers:
     Authorization: Bearer <IL_TUO_TOKEN>
     Accept: application/vnd.github+json
   Body:
     {"ref": "main"}
   ```

## Setup

```bash
pip install -r requirements.txt
python scraper.py
```

Poi, su GitHub:

1. Push del repo su `main` (repo già creato: https://github.com/mbmichele/ecomuseo_mantova).
2. Impostazioni repo → Pages → Source: branch `main`, cartella `/docs`.
3. Il feed sarà disponibile su `https://mbmichele.github.io/ecomuseo_mantova/feed.xml`.
4. Configura il cron esterno come descritto sopra.

## Prompt di generazione

Questo repository è stato generato da Claude a partire dal seguente prompt dell'utente:

> Crea un repo per gist che crea un flusso rss degli articoli che vengono pubblicato alla pagina https://www.ecomuseomantova.it/news-eventi/pagina-1.
> Devono esserci cron esterni ed interni tutti fi un'ora.
> Nel file readme inserisci anche il promp di generazione
