# Wasatch Wire

Daily curated Salt Lake Valley / Utah + tech + dev news, published to vPages at
https://crowdersoup.vpages.site/wasatch-wire/

A Claude scheduled task runs every morning (5:33am MT):

1. `python3 src/fetch_feeds.py src/feeds.json candidates.json --site $SITE` — pulls all feeds, drops URLs used in the last 7 editions.
2. Claude curates `edition.json` following `src/CURATION.md`.
3. `python3 src/render.py edition.json candidates.json dist --site $SITE` — renders the static site.
4. `dist/` is patch-published to vPages; the edition JSON is committed to `editions/`.

Edit `src/feeds.json` to change sources and `src/CURATION.md` to change editorial taste.

## License

Code is MIT licensed — see [LICENSE](LICENSE). Linked articles and their headlines belong to their respective publishers.
