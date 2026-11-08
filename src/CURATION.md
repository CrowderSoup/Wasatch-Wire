# Wasatch Wire — curation guide

Reader: Aaron, a Millcreek (Salt Lake Valley) software engineer/architect — Go, Python/Django, HTMX, cloud infra, homelab, legal tech.

## Edition shape (~20–28 stories)
- **top** "Top Stories" — 3 stories: the 2 biggest Salt Lake/Utah stories plus the single most important tech story (or 3 local if tech is quiet).
- **local** "Salt Lake & Utah" — 8–11. Prioritise Salt Lake Valley, then statewide: Legislature/government, public safety affecting the valley, growth/housing/transit, water/Great Salt Lake/weather, outdoors, notable sports results (one item per game, not five). Skip national/world wire stories that KSL republishes unless they have a Utah angle. Skip opinion pieces, letters, listicles, archive reprints and sponsored posts.
- **tech** "Tech" — 8–10. Weight Hacker News by points; include notable Lobsters threads, security advisories that affect common stacks, AI industry news, homelab/self-hosting, open source, legal tech. Skip product deals, gadget reviews and gaming promos.
- **dev** "Dev Corner" — 4–6 from Go, Django/Python, Simon Willison, and dev-flavoured Lobsters/HN posts (tools, version control, languages). Releases and security releases first.

## Rules
- Don't repeat a story already in the last 7 editions (fetch_feeds.py excludes exact URLs; also skip obvious same-story repeats under new URLs unless there's a real development).
- Merge duplicate coverage into one story: pick the most complete source as `url`, list the others in `also` (max 3).
- Prefer stories from the last 24 hours; Dev Corner may reach back 7 days.
- `summary`: 1–2 sentences, max ~40 words, written in your own words from the feed snippet/title. Never copy feed text verbatim beyond a short name or figure. Neutral, factual tone; no editorialising on politics. Don't invent details not in the snippet/title — if a community post has no snippet, describe what the title/URL makes clear and keep it short.
- Keep the original headline as `title` (fix only obvious entity encoding).
- `source` must be the outlet name exactly as in feeds.json.
