#!/usr/bin/env python3
"""Survey data sources: fetch robots.txt + terms/license/API-doc pages and store evidence.

Stdlib + PyYAML only. GET requests only, >=1s between requests, identifying User-Agent.
It never calls an API in bulk and never follows links. Evidence per source/page:
status, final URL, headers (subset), sha256, first 200 KB of body. Legal judgement is NOT
made here; a human reads the evidence and fills docs/sources/SOURCES.md.

Usage:  python scripts/probe_sources.py --contact you@example.com [--only nvd,osv]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "docs/sources/candidates.yaml"
EVIDENCE = ROOT / "docs/sources/evidence"
MAX_BODY = 200_000
DELAY = 1.0
KEEP_HEADERS = ("content-type", "content-length", "last-modified", "etag", "retry-after",
                "x-ratelimit-limit", "x-ratelimit-remaining")


def fetch(url: str, ua: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    out: dict = {"url": url, "fetched_at": dt.datetime.now(dt.UTC).isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(MAX_BODY)
            out.update(status=r.status, final_url=r.geturl(),
                       headers={k: v for k, v in r.headers.items() if k.lower() in KEEP_HEADERS})
    except urllib.error.HTTPError as e:
        body = e.read(MAX_BODY) if e.fp else b""
        out.update(status=e.code, final_url=url, headers={})
    except Exception as e:  # network blocked, DNS, TLS ...
        body = b""
        out.update(status=None, error=f"{type(e).__name__}: {e}")
    out["sha256"] = hashlib.sha256(body).hexdigest()
    out["bytes"] = len(body)
    out["_body"] = body
    time.sleep(DELAY)
    return out


def slug(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", url.split("://", 1)[-1])[:80].strip("_")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact", required=True, help="contact string for the User-Agent")
    ap.add_argument("--only", help="comma separated source ids")
    a = ap.parse_args()
    ua = f"opsgraph-source-survey/0.1 (+contact: {a.contact})"
    only = set(a.only.split(",")) if a.only else None
    today = dt.date.today().isoformat()
    summary = []

    for s in yaml.safe_load(CANDIDATES.read_text(encoding="utf-8"))["sources"]:
        if only and s["id"] not in only:
            continue
        d = EVIDENCE / s["id"] / today
        d.mkdir(parents=True, exist_ok=True)
        rec = {"id": s["id"], "robots": [], "pages": [], "sample_allowed_by_robots": None}

        for host in s.get("robots_hosts", []):
            r = fetch(host.rstrip("/") + "/robots.txt", ua)
            (d / f"robots_{slug(host)}.txt").write_bytes(r.pop("_body"))
            rec["robots"].append({k: v for k, v in r.items()})
            if s.get("sample_target") and s["sample_target"].startswith(host) and r.get("status") == 200:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse((d / f"robots_{slug(host)}.txt").read_text(errors="replace").splitlines())
                rec["sample_allowed_by_robots"] = rp.can_fetch(ua, s["sample_target"])
                rec["crawl_delay"] = rp.crawl_delay(ua)

        urls = [u for lst in s.get("pages", {}).values() for u in lst]
        if s.get("sample_target"):
            urls.append(s["sample_target"])
        for u in urls:
            r = fetch(u, ua)
            (d / f"page_{slug(u)}.html").write_bytes(r.pop("_body"))
            rec["pages"].append(r)
        (d / "probe.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        ok = sum(1 for p in rec["pages"] if p.get("status") == 200)
        print(f"{s['id']:<18} pages ok {ok}/{len(rec['pages'])}  robots "
              f"{[r.get('status') for r in rec['robots']]}")
        summary.append(rec)

    print(f"\nEvidence saved under {EVIDENCE.relative_to(ROOT)}. Review it, then fill SOURCES.md.")


if __name__ == "__main__":
    main()
