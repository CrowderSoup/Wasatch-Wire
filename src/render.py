#!/usr/bin/env python3
"""Render a curated edition into the static site.

Usage: python3 render.py edition.json candidates.json dist/ [--site URL]

edition.json schema:
{"date": "YYYY-MM-DD", "sections": [{"id": "top|local|tech|dev", "title": "...",
  "stories": [{"title": "...", "url": "...", "source": "...", "summary": "...",
               "also": [{"source": "...", "url": "..."}]}]}]}
discuss_url/points are filled from candidates.json by URL when missing.
With --site, the existing editions/index.json is fetched so the archive keeps past dates.
"""
import datetime as dt, html, json, os, shutil, sys, urllib.request
from email.utils import format_datetime

SITE_TITLE = "Wasatch Wire"
TAGLINE = "Salt Lake, Utah &amp; tech — curated every morning"
ICON = {"top": "★", "local": "⛰", "tech": "⌁", "dev": "{ }"}
e = lambda s: html.escape(s or "", quote=True)

def nice_date(d):
    return dt.date.fromisoformat(d).strftime("%A, %B %-d, %Y")

def page(title, body, root, desc=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="{root}style.css">
<link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="{root}feed.xml">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⛰</text></svg>">
</head><body>
<header class="mast"><a class="brand" href="{root}">{SITE_TITLE}</a><p class="tag">{TAGLINE}</p>
<nav><a href="{root}">Today</a><a href="{root}archive/">Archive</a><a href="{root}feed.xml">RSS</a></nav></header>
<main>{body}</main>
<footer><p>Headlines and links belong to their publishers; summaries are AI-written from feed excerpts — click through for the full story.</p>
<p>Built daily by Claude on <a href="https://crowdersoup.vpages.site/">vPages</a> · <a href="https://crowdersoup.com">crowdersoup.com</a></p></footer>
</body></html>"""

def story_html(s, lead=False):
    meta = [f'<span class="src">{e(s["source"])}</span>']
    for a in s.get("also", []):
        meta.append(f'<a class="also" href="{e(a["url"])}">{e(a["source"])}</a>')
    if s.get("discuss_url"):
        label = f'{s["points"]} pts · discuss' if s.get("points") else "discuss"
        meta.append(f'<a class="disc" href="{e(s["discuss_url"])}">{label}</a>')
    return f"""<article class="story{' lead' if lead else ''}">
<h3><a href="{e(s["url"])}">{e(s["title"])}</a></h3>
<p class="sum">{e(s.get("summary"))}</p>
<p class="meta">{" · ".join(meta)}</p></article>"""

def edition_body(ed, dates):
    n = sum(len(s["stories"]) for s in ed["sections"])
    out = [f'<div class="dateline"><time datetime="{ed["date"]}">{nice_date(ed["date"])}</time><span>{n} stories</span></div>']
    if ed.get("lede"):
        out.append(f'<p class="lede">{e(ed["lede"])}</p>')
    out.append('<nav class="jump">' + "".join(
        f'<a href="#{s["id"]}">{e(s["title"])}</a>' for s in ed["sections"]) + "</nav>")
    for s in ed["sections"]:
        lead = s["id"] == "top"
        out.append(f'<section id="{s["id"]}" class="sec sec-{s["id"]}"><h2><span>{ICON.get(s["id"], "")}</span> {e(s["title"])}</h2>'
                   + "".join(story_html(x, lead) for x in s["stories"]) + "</section>")
    i = dates.index(ed["date"]) if ed["date"] in dates else -1
    nav = []
    if i >= 0 and i + 1 < len(dates):
        nav.append(f'<a href="ROOTarchive/{dates[i+1]}.html">← {nice_date(dates[i+1])}</a>')
    if i > 0:
        nav.append(f'<a href="ROOTarchive/{dates[i-1]}.html">{nice_date(dates[i-1])} →</a>')
    if nav:
        out.append('<nav class="pager">' + "".join(nav) + "</nav>")
    return "\n".join(out)

def fetch_json(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read())

def main():
    ed_path, cand_path, dist = sys.argv[1:4]
    site = sys.argv[sys.argv.index("--site") + 1].rstrip("/") if "--site" in sys.argv else None
    ed = json.load(open(ed_path))
    cands = {}
    if os.path.exists(cand_path):
        for items in json.load(open(cand_path))["sections"].values():
            for c in items: cands[c["url"]] = c
    for s in ed["sections"]:
        for st in s["stories"]:
            c = cands.get(st["url"], {})
            st.setdefault("discuss_url", c.get("discuss_url"))
            st.setdefault("points", c.get("points"))
            st.setdefault("also", [])
    ed.setdefault("generated_at", dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"))

    dates = []
    if site:
        try: dates = fetch_json(site + "/editions/index.json").get("dates", [])
        except Exception as ex: print("note: no existing index.json:", ex)
    dates = sorted(set(dates) | {ed["date"]}, reverse=True)

    os.makedirs(f"{dist}/archive", exist_ok=True); os.makedirs(f"{dist}/editions", exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(here, "style.css"), f"{dist}/style.css")

    body = edition_body(ed, dates)
    title = f"{SITE_TITLE} — {nice_date(ed['date'])}"
    desc = "; ".join(s["title"] for s in ed["sections"][0]["stories"][:3])
    is_latest = ed["date"] == dates[0]
    if is_latest:
        open(f"{dist}/index.html", "w").write(page(title, body.replace("ROOT", ""), "", desc))
    open(f"{dist}/archive/{ed['date']}.html", "w").write(page(title, body.replace("ROOT", "../"), "../", desc))
    json.dump(ed, open(f"{dist}/editions/{ed['date']}.json", "w"), indent=1, ensure_ascii=False)
    # re-render the previous edition's page so its pager links forward to this one
    i = dates.index(ed["date"])
    if site and i + 1 < len(dates):
        try:
            prev = fetch_json(f"{site}/editions/{dates[i+1]}.json")
            ptitle = f"{SITE_TITLE} — {nice_date(prev['date'])}"
            open(f"{dist}/archive/{prev['date']}.html", "w").write(
                page(ptitle, edition_body(prev, dates).replace("ROOT", "../"), "../"))
        except Exception as ex:
            print("note: could not re-render previous edition:", ex)
    json.dump({"dates": dates}, open(f"{dist}/editions/index.json", "w"))

    items = "".join(f'<li><a href="{d}.html">{nice_date(d)}</a></li>' for d in dates)
    open(f"{dist}/archive/index.html", "w").write(page(f"Archive — {SITE_TITLE}",
        f'<h2 class="arch-h">Past editions</h2><ul class="archive">{items}</ul>', "../"))

    if is_latest and site:
        pub = format_datetime(dt.datetime.combine(dt.date.fromisoformat(ed["date"]), dt.time(13, 0), dt.timezone.utc))
        lis = "".join(f"<li><a href='{e(st['url'])}'>{e(st['title'])}</a> ({e(st['source'])}) — {e(st.get('summary'))}</li>"
                      for s in ed["sections"] for st in s["stories"])
        feed = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>{SITE_TITLE}</title><link>{site}/</link>
<description>Daily curated Salt Lake, Utah and tech news</description>
<item><title>{e(title)}</title><link>{site}/archive/{ed['date']}.html</link><guid>{site}/archive/{ed['date']}.html</guid>
<pubDate>{pub}</pubDate><description>{e('<ul>' + lis + '</ul>')}</description></item>
</channel></rss>"""
        open(f"{dist}/feed.xml", "w").write(feed)
    print("rendered", ed["date"], "latest" if is_latest else "(archive only)", "dates:", len(dates))

if __name__ == "__main__":
    main()
