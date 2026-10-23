# Changelog

Versioning semantico (MAJOR.MINOR.PATCH).

## v1.4.0 — 2026-10-20
- Fix: i fallimenti del job dovuti a errori temporanei del sito (HTTP 5xx/429, connessioni interrotte) non erano gestiti dai retry. Ora si ritenta fino a 4 volte su timeout, errori di rete e HTTP 408/425/429/5xx.
- Se il sito resta irraggiungibile il job non fallisce più: avviso `::warning::` e feed precedente invariato. Restano errori (job rosso) 403/404 e "0 elementi trovati".
- Fix: il confronto del feed ignora `lastBuildDate` (prima il feed risultava sempre modificato e veniva committato ogni ora, con un deploy di Pages ogni volta).
- Workflow: runner fissato a `ubuntu-24.04` (migrazione di `ubuntu-latest` a Ubuntu 26), `timeout-minutes: 15`, `concurrency` con coda per cron interno/esterno.
- README: sezione "Risoluzione problemi" e prompt di rigenerazione aggiornati.

## v1.3.1 — 2026-10-14
- README: rimossa l'indicazione dello strumento usato per generare il repository.

## v1.3.0 — 2026-10-02
- Fix: timeout di rete verso ecomuseomantova.it (`ReadTimeout`) non più fatale — lo scraper ora ritenta fino a 3 volte (con backoff crescente) prima di fallire, e il timeout per richiesta è salito da 30 a 45s.

## v1.2.0 — 2026-09-28
- Fix: rimosso `br` da `Accept-Encoding` (causava 0 elementi trovati: la risposta arrivava compressa in Brotli, non decomprimibile senza il pacchetto `brotli`/`brotlicffi`).
- Aggiunto log dello status/dimensione/content-encoding della risposta HTTP nello scraper, per diagnosticare più in fretta eventuali problemi futuri.
- Aggiunto `docs/.nojekyll` per tenere la cartella `docs/` tracciata da git fin dal primo commit e disattivare il build Jekyll automatico di GitHub Pages, che falliva con "No such file or directory ... /docs".
- README: nuova sezione "Risoluzione problemi".

## v1.1.0 — 2026-09-28
- README: link resi cliccabili e copiabili (formato `[url](url)`).
- README: aggiunto il "Prompt di rigenerazione completo", con tutti i requisiti raccolti nel corso della conversazione, oltre al prompt di generazione originale.

## v1.0.0 — 2026-09-28
- Prima versione: scraper della pagina news/eventi di Ecomuseo Mantova, generazione feed RSS in `docs/feed.xml`, pubblicazione via GitHub Pages.
- GitHub Action con cron interno orario + `workflow_dispatch` per il cron esterno (cron-job.org), con retry/fetch+rebase sul push in caso di conflitto fra i due trigger.
- Dump automatico dell'HTML di debug quando lo scraping non trova elementi.
