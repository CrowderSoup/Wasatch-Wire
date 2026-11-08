#!/usr/bin/env python3
"""Fetch all feeds and write candidates.json for curation.

Usage: python3 fetch_feeds.py feeds.json candidates.json [--site URL]
With --site, URLs that appeared in the last 7 published editions are excluded.
"""
import calendar, html, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import feedparser

UA = {"User-Agent": "Mozilla/5.0 (WasatchWire daily digest)"}

def get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

def clean(text, n=320):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text[:n] + ("…" if len(text) > n else "")

def entry_time(e):
    for k in ("published_parsed", "updated_parsed"):
        if e.get(k):
            return calendar.timegm(e[k])
    return None

def fetch(feed):
    try:
        return feed, feedparser.parse(get(feed["url"])), None
    except Exception as ex:
        return feed, None, str(ex)

def seen_urls(site):
    urls = set()
    try:
        idx = json.loads(get(site.rstrip("/") + "/editions/index.json"))
        for d in idx.get("dates", [])[:7]:
            ed = json.loads(get(f"{site.rstrip('/')}/editions/{d}.json"))
            for s in ed["sections"]:
                for st in s["stories"]:
                    urls.add(st["url"])
    except Exception as ex:
        print(f"note: could not load past editions ({ex})", file=sys.stderr)
    return urls

def main():
    cfg_path, out_path = sys.argv[1], sys.argv[2]
    site = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else None
    cfg = json.load(open(cfg_path))
    exclude = seen_urls(site) if site else set()
    now = time.time()
    jobs = [(s, f) for s in cfg["sections"] for f in s["feeds"]]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda sf: (sf[0], *fetch(sf[1])), jobs))
    out, errors, seen = {s["id"]: [] for s in cfg["sections"]}, [], set()
    for sec, feed, parsed, err in results:
        if err or parsed is None:
            errors.append({"feed": feed["name"], "error": err}); continue
        for e in parsed.entries:
            t = entry_time(e)
            if t and now - t > sec["max_age_hours"] * 3600:
                continue
            link = e.get("link", "")
            desc = e.get("summary", "")
            discuss = None
            if feed.get("community"):
                discuss = e.get("comments")
                m = re.search(r'Article URL:\s*<a href="([^"]+)"', desc)
                if m: link = html.unescape(m.group(1))
            if not link or link in exclude or link in seen:
                continue
            seen.add(link)
            pts = re.search(r"Points:\s*(\d+)", desc)
            cm = re.search(r"# Comments:\s*(\d+)", desc)
            out[sec["id"]].append({
                "source": feed["name"], "title": clean(e.get("title", ""), 200), "url": link,
                "discuss_url": discuss, "published": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(t)) if t else None,
                "points": int(pts.group(1)) if pts else None, "comments": int(cm.group(1)) if cm else None,
                "snippet": "" if feed.get("community") else clean(desc),
            })
    json.dump({"generated": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "errors": errors,
               "sections": out}, open(out_path, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {out_path}: " + ", ".join(f"{k}={len(v)}" for k, v in out.items()) + f"; errors={len(errors)}")
    for e in errors: print("  ERR", e["feed"], e["error"][:100])

if __name__ == "__main__":
    main()
