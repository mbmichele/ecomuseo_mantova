# Changelog

Versioning semantico (MAJOR.MINOR.PATCH).

## v1.0.0 — 2026-09-28
- Prima versione: scraper della pagina news/eventi di Ecomuseo Mantova, generazione feed RSS in `docs/feed.xml`, pubblicazione via GitHub Pages.
- GitHub Action con cron interno orario + `workflow_dispatch` per il cron esterno (cron-job.org), con retry/fetch+rebase sul push in caso di conflitto fra i due trigger.
- Dump automatico dell'HTML di debug quando lo scraping non trova elementi.
