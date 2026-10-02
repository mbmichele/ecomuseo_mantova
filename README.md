# ecomuseo_mantova

**Versione: v1.3.0** — vedi [CHANGELOG.md](CHANGELOG.md)

[![Aggiorna feed RSS](https://github.com/mbmichele/ecomuseo_mantova/actions/workflows/update-feed.yml/badge.svg)](https://github.com/mbmichele/ecomuseo_mantova/actions/workflows/update-feed.yml)

Feed RSS **non ufficiale** delle news/eventi pubblicati da Ecomuseo di Mantova, generato tramite scraping (il sito non offre un feed proprio).

- Repo: [https://github.com/mbmichele/ecomuseo_mantova](https://github.com/mbmichele/ecomuseo_mantova)
- Pagina sorgente: [https://www.ecomuseomantova.it/news-eventi/pagina-1](https://www.ecomuseomantova.it/news-eventi/pagina-1)
- Feed pubblicato (dopo aver attivato GitHub Pages): [https://mbmichele.github.io/ecomuseo_mantova/feed.xml](https://mbmichele.github.io/ecomuseo_mantova/feed.xml)

## Come funziona

1. `scraper.py` scarica [https://www.ecomuseomantova.it/news-eventi/pagina-1](https://www.ecomuseomantova.it/news-eventi/pagina-1) (simulando un accesso da browser Firefox 156), estrae titolo, link, descrizione/luogo e data di ogni news (dai blocchi `div.col444 > div.blk-txt`) e genera un feed RSS 2.0 in `docs/feed.xml` (max 50 elementi). La data mostrata sul sito è la data dell'evento/news, non un timestamp di pubblicazione, e viene usata come `pubDate` del feed.
2. Il feed viene pubblicato staticamente tramite **GitHub Pages** dalla cartella `/docs` del branch `main`.
3. Una GitHub Action rigenera il feed **ogni ora** e fa commit/push solo se il contenuto è cambiato.
4. Se lo scraping non trova elementi (es. il sito cambia struttura o mostra una pagina anti-bot), l'HTML ricevuto viene salvato come artifact del workflow per il debug, invece di fallire senza spiegazioni.

## Doppio cron: interno + esterno

L'aggiornamento orario è garantito da due meccanismi indipendenti, entrambi impostati a un'ora:

- **Cron interno di GitHub Actions**: `schedule: cron: "0 * * * *"` nel workflow `.github/workflows/update-feed.yml`. È il meccanismo principale, ma GitHub può ritardarlo nei momenti di carico.
- **Cron esterno** ([https://cron-job.org](https://cron-job.org), ogni ora): fa da backup/rinforzo chiamando l'API di GitHub per lanciare lo stesso workflow via `workflow_dispatch`, così l'aggiornamento non dipende solo dallo scheduler interno di GitHub.

Poiché i due cron possono scattare quasi in contemporanea, il workflow gestisce l'eventuale conflitto sul push (commit "arrivato prima" dall'altra esecuzione) con **fetch + rebase e retry automatico**, invece di fallire.

Per configurare il cron esterno su cron-job.org:

1. Crea un Personal Access Token: [https://github.com/settings/tokens](https://github.com/settings/tokens) — permesso `repo` (o un fine-grained token con permesso "Actions: write" su questo repo).
2. Su cron-job.org crea un job orario che esegue una richiesta:

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

1. Push del repo su `main` (repo già creato: [https://github.com/mbmichele/ecomuseo_mantova](https://github.com/mbmichele/ecomuseo_mantova)).
2. Impostazioni repo → Pages → Source: branch `main`, cartella `/docs`.
3. Il feed sarà disponibile su [https://mbmichele.github.io/ecomuseo_mantova/feed.xml](https://mbmichele.github.io/ecomuseo_mantova/feed.xml).
4. Configura il cron esterno come descritto sopra.

## Risoluzione problemi

- **Lo scraper trova 0 elementi pur senza errori HTTP**: quasi sempre è perché la risposta arriva compressa in un formato che `requests` non riesce a decomprimere (es. Brotli, se il pacchetto `brotli`/`brotlicffi` non è installato). Per questo l'header `Accept-Encoding` dichiara solo `gzip, deflate` (che `requests` gestisce sempre nativamente) e **non** `br`. Se succede di nuovo, controlla nel log dell'Action la riga `GET ... -> status, bytes, content-encoding=...` e il file `debug_last_response.html` caricato come artifact del workflow in caso di fallimento.
- **Il job fallisce con `requests.exceptions.ReadTimeout`**: è un timeout di rete transitorio verso il sito (non un bug del parser). Lo scraper ritenta automaticamente fino a 3 volte con backoff crescente prima di arrendersi; se fallisce comunque, aspetta il run successivo (orario) o rilancialo a mano.
- **Il workflow automatico "pages build and deployment" fallisce con `No such file or directory ... /docs`**: è il build Jekyll che GitHub avvia da solo quando Pages è configurato come "Deploy from a branch". Fallisce se la cartella `/docs` non esiste ancora nel repo (git non traccia cartelle vuote) o se GitHub prova comunque a processarla con Jekyll. Il file `docs/.nojekyll` (vuoto, già incluso nel repo) risolve entrambe le cose: tiene la cartella tracciata fin dal primo commit e disattiva il build Jekyll, lasciando `feed.xml` servito così com'è.

## Prompt di generazione originale

Questo repository è stato generato da Claude a partire dal seguente prompt dell'utente:

> Crea un repo per gist che crea un flusso rss degli articoli che vengono pubblicato alla pagina https://www.ecomuseomantova.it/news-eventi/pagina-1.
> Devono esserci cron esterni ed interni tutti fi un'ora.
> Nel file readme inserisci anche il promp di generazione

## Prompt di rigenerazione completo

Prompt unico, autosufficiente, con tutti i requisiti raccolti nel corso della conversazione: da usare per ricreare questo repository da zero con un altro assistente o in una nuova sessione.

> Crea un repository che generi un feed RSS non ufficiale a partire dallo scraping della pagina elenco news/eventi `https://www.ecomuseomantova.it/news-eventi/pagina-1` (il sito non offre un feed proprio; pagina 1 = le news più recenti).
>
> Requisiti:
> - Scraper Python (`requests` + `BeautifulSoup`) che estrae da ogni blocco `div.col444 > div.blk-txt` della pagina: titolo e link (da `h3 a`), descrizione (da `p`, con fallback sul luogo preso dal link `news-eventi/filtra/...` dentro `h5` se la descrizione è vuota), e data in formato `gg.mm.aaaa` (usata come `pubDate` del feed, essendo la data dell'evento/news e non un timestamp di pubblicazione).
> - Generazione di un feed RSS 2.0 valido (es. con `feedgen`) in `docs/feed.xml`, max 50 elementi, pubblicato staticamente tramite GitHub Pages (branch `main`, cartella `/docs`).
> - Lo scraper deve simulare un accesso da browser **Firefox 156** (header HTTP completi: User-Agent, Accept, Accept-Language, Accept-Encoding, Sec-Fetch-*, ecc.), non solo uno User-Agent nudo.
> - Se lo scraping non trova elementi, salvare l'HTML ricevuto in un file di debug (e caricarlo come artifact del workflow) invece di fallire senza diagnostica.
> - Doppio cron orario indipendente: cron interno di GitHub Actions (`schedule: cron: "0 * * * *"`) **e** cron esterno su **cron-job.org** che chiama l'API di GitHub (`POST .../actions/workflows/<file>.yml/dispatches`) per innescare lo stesso workflow via `workflow_dispatch`.
> - Il workflow deve fare commit/push del feed solo se il contenuto è cambiato, e gestire con **fetch + rebase e retry automatico** l'eventuale conflitto di push fra i due cron che scattano quasi in contemporanea.
> - Nel README: spiegazione del funzionamento, istruzioni di setup/Pages, istruzioni per configurare il cron esterno su cron-job.org, link cliccabili e copiabili (formato `[url](url)`), sia il prompt di generazione originale sia questo prompt di rigenerazione.
> - Versioning semantico (MAJOR.MINOR.PATCH) con `CHANGELOG.md`, numero di versione indicato nel README, e nome del file del pacchetto/zip consegnato che include sempre il numero di versione (es. `ecomuseo-mantova-rss-v1.0.0.zip`).
