#!/usr/bin/env python3
"""
scrape_decline_index.py   –   v3.2  (2025-07-18)

• Читает table_on_ramp.csv  → формирует список агрегаторов
• После КАЖДОГО обработанного бренда добавляет строку в decline_index.csv
• При перезапуске пропускает уже сохранённые бренды и продолжает работу
• По завершении пересортирует CSV по колонке decline_index (атомарно)

✓  Cloudflare-safe, Proxy-aware, Unicode-aware, 15-min hard timeout
"""

from __future__ import annotations
import csv, os, random, re, sys, time, signal, logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    import cloudscraper                              # обход Cloudflare
except ImportError:
    cloudscraper = None

# ── CONSTANTS ─────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent
CSV_TABLE   = ROOT / "table_on_ramp.csv"
CSV_OUTPUT  = ROOT / "decline_index.csv"
UA          = ("Mozilla/5.0 (Linux; rv:128.0) Gecko/20100101 "
               "Firefox/128.0 decline-bot/3.2")
HEADERS     = {"User-Agent": UA}
TIMEOUT     = 15
MAX_RETRIES = 3
SLEEP_RANGE = (1.2, 2.2)
HARD_LIMIT  = 900                                   # 15 мин

PUSHSHIFT_TOKEN = os.getenv("PUSHSHIFT_TOKEN")
PROXY           = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
PROXIES         = {"http": PROXY, "https": PROXY} if PROXY else None

DECLINE_RE = re.compile(
    r"(declin\w*|fail\w*|reject\w*|deni\w*|error|abgelehnt|rechazad[oa])",
    re.I,
)

# ── LOGGING ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("decline-index")

# ── GLOBAL TIMEOUT (safety) ───────────────────────────────────────────────
def _alarm(_sig, _frm):
    log.critical("⏰ 15-minute timeout reached — aborting!")
    sys.exit(1)

signal.signal(signal.SIGALRM, _alarm)
signal.alarm(HARD_LIMIT)

# ── UTILITIES ─────────────────────────────────────────────────────────────
def append_row(path: Path, row: list, header: list[str]) -> None:
    """Добавляет строку в CSV; создаёт файл с заголовком при первом вызове."""
    new_file = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        if new_file:
            writer.writerow(header)
        writer.writerow(row)

def _get(url: str, *, as_json=False, hdrs: Optional[Dict] = None):
    """HTTP-GET с retry, proxy, Cloudflare-bypass и логом ошибок."""
    session: requests.Session | cloudscraper.CloudScraper
    if cloudscraper:
        try:
            session = cloudscraper.create_scraper(
                browser={"browser": "firefox", "platform": "windows", "mobile": False}
            )
        except Exception:                                     # fallback → requests
            session = requests
    else:
        session = requests

    headers = HEADERS | (hdrs or {})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, headers=headers, timeout=TIMEOUT, proxies=PROXIES)
            r.raise_for_status()
            return r.json() if as_json else r.text
        except Exception as exc:
            if attempt == MAX_RETRIES:
                log.warning("  [%s] %s", url, exc)
                return {} if as_json else ""
            time.sleep(1.4 * attempt)

def decline_ratio(texts: List[str]) -> float:
    if not texts:
        return 0.0
    hits = sum(bool(DECLINE_RE.search(t)) for t in texts)
    return round(hits / len(texts), 3)

# ── LOAD AGGREGATORS & TP DOMAINS ─────────────────────────────────────────
if not CSV_TABLE.exists():
    log.critical("table_on_ramp.csv not found: %s", CSV_TABLE)
    sys.exit(1)

tbl = pd.read_csv(CSV_TABLE)

name_col = next((c for c in tbl.columns
                 if c.lower().startswith("agg") or c.lower() == "name"), None)
if not name_col:
    log.critical("No column like 'agg*' or 'name' in CSV — abort")
    sys.exit(1)

AGGREGATORS = sorted(tbl[name_col].dropna().unique())

# — домены для Trustpilot
domain_cols = [c for c in tbl.columns if any(k in c.lower() for k in ("site", "url", "domain"))]
TP_SLUG: Dict[str, str] = {}
for _, row in tbl.iterrows():
    brand = str(row[name_col]).strip()
    for dc in domain_cols:
        url = str(row.get(dc, ""))
        m = re.search(r"https?://([^/]+)/?", url)
        if m:
            TP_SLUG[brand] = m.group(1)
            break
TP_SLUG.update({"Mercuryo": "mercuryo.io", "Utorg": "utorg.pro"})

# ── RESUME-MODE ───────────────────────────────────────────────────────────
done: set[str] = set()
if CSV_OUTPUT.exists():
    with CSV_OUTPUT.open() as f:
        done = {row.split(",")[0] for row in f.readlines()[1:]}
    AGGREGATORS = [b for b in AGGREGATORS if b not in done]
    if done:
        log.info("Resume mode: %d brands already done → %d left",
                 len(done), len(AGGREGATORS))

log.info("Loaded %d aggregators total", len(done) + len(AGGREGATORS))

# ── SCRAPERS ──────────────────────────────────────────────────────────────
def trustpilot_reviews(brand: str, pages: int = 2) -> List[str]:
    slug = TP_SLUG.get(brand, f"{brand.lower()}.com")
    texts: List[str] = []
    for p in range(1, pages + 1):
        html = _get(f"https://www.trustpilot.com/review/{slug}?page={p}")
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")
        texts += [p.get_text(strip=True).lower() for p in soup.select("p")]
        time.sleep(random.uniform(*SLEEP_RANGE))
    return texts

def reddit_comments(brand: str, size: int = 100) -> List[str]:
    comments: List[str] = []

    if PUSHSHIFT_TOKEN:
        url = ( "https://api.pushshift.io/reddit/search/comment/"
                f"?q={brand}%20declined&size={size}&fields=body")
        hdr = {"Authorization": f"Bearer {PUSHSHIFT_TOKEN}"}
        data = _get(url, as_json=True, hdrs=hdr).get("data", [])
        comments = [d.get("body", "").lower() for d in data]

    if not comments:
        url = ("https://www.reddit.com/search.json"
               f"?q={brand}+declined&type=comment&limit={size}&raw_json=1")
        js = _get(url, as_json=True)
        for ch in js.get("data", {}).get("children", []):
            data = ch.get("data", {})
            text = data.get("body") or data.get("selftext") or ""
            if text:
                comments.append(text.lower())
    return comments

# ── MAIN LOOP ─────────────────────────────────────────────────────────────
header = ["aggregator", "trustpilot", "reddit", "decline_index"]
new_rows: List[list] = []

for brand in AGGREGATORS:
    log.info("→ %s", brand)

    tp = trustpilot_reviews(brand)
    tp_ratio = decline_ratio(tp)
    log.info("  Trustpilot: %4d revs, ratio=%.3f", len(tp), tp_ratio)

    rd = reddit_comments(brand)
    rd_ratio = decline_ratio(rd)
    log.info("  Reddit:     %4d cmts, ratio=%.3f", len(rd), rd_ratio)

    row = [brand, tp_ratio, rd_ratio, round((tp_ratio + rd_ratio) / 2, 3)]
    append_row(CSV_OUTPUT, row, header)
    new_rows.append(row)

# ── FINAL SORT (атомарно) ─────────────────────────────────────────────────
if CSV_OUTPUT.exists():
    df_final = pd.read_csv(CSV_OUTPUT)
    df_final = df_final.sort_values("decline_index")
    tmp = CSV_OUTPUT.with_suffix(".tmp")
    df_final.to_csv(tmp, index=False, lineterminator="\n", float_format="%.3f")
    tmp.replace(CSV_OUTPUT)
    log.info("✅  decline_index.csv sorted & saved — %d rows total", len(df_final))
else:
    log.warning("No CSV created — nothing scraped?")
