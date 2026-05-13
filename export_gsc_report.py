"""
Export DTFPrinterUSA Google Search Console data for the report.

Outputs report-ready CSVs into ./data:
- gsc-trend.csv
- gsc-by-pagetype.csv
- gsc-pages.csv
- gsc-pages-monthly.csv
- gsc-queries.csv
- gsc-kpis.csv
- gsc-keywords-monthly.csv
- gsc-keywords-exact.csv
- gsc-keyword-variants.csv
"""

from __future__ import annotations

import csv
import os
import re
import time
from calendar import monthrange
from collections import defaultdict
from datetime import date
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = Path(__file__).resolve().parent
DATA_DIR = REPORT_DIR / "data"

PROPERTY = "sc-domain:dtfprinterusa.com"
SERVICE_ACCOUNT_FILE = BASE_DIR / "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
ROW_LIMIT = 25000

TREND_START = (2025, 4)
TREND_END = (2026, 4)
KEYWORD_START = (2025, 11)
KEYWORD_END = (2026, 4)
VARIANT_MONTH = (2026, 4)

AHREFS_KEYWORDS_FILE = DATA_DIR / "dtfprinterusa-ahrefs-keywords.csv"


def service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=creds)


def months_between(start: tuple[int, int], end: tuple[int, int]):
    year, month = start
    while (year, month) <= end:
        yield year, month
        month += 1
        if month > 12:
            year += 1
            month = 1


def month_dates(year: int, month: int) -> tuple[str, str]:
    return (
        date(year, month, 1).isoformat(),
        date(year, month, monthrange(year, month)[1]).isoformat(),
    )


def month_label(year: int, month: int) -> str:
    return date(year, month, 1).strftime("%b '%y")


def month_key(year: int, month: int) -> str:
    return date(year, month, 1).strftime("%b%y").lower()


def query_gsc(svc, start_date, end_date, dimensions=None, filters=None):
    rows = []
    start_row = 0
    while True:
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "rowLimit": ROW_LIMIT,
            "startRow": start_row,
            "dataState": "final",
        }
        if dimensions:
            body["dimensions"] = dimensions
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        resp = svc.searchanalytics().query(siteUrl=PROPERTY, body=body).execute()
        batch = resp.get("rows", [])
        rows.extend(batch)
        if len(batch) < ROW_LIMIT:
            break
        start_row += ROW_LIMIT
        time.sleep(0.2)
    return rows


def weighted_position(total):
    den = total.get("pos_den", 0)
    return round(total["pos_num"] / den, 2) if den else 0


def ctr_pct(clicks, impressions):
    return round(clicks / impressions * 100, 4) if impressions else 0


def add_metrics(total, row):
    impressions = int(row.get("impressions", 0))
    clicks = int(row.get("clicks", 0))
    position = float(row.get("position", 0))
    total["impressions"] += impressions
    total["clicks"] += clicks
    if impressions and position:
        total["pos_num"] += position * impressions
        total["pos_den"] += impressions


def metric_bucket():
    return {"impressions": 0, "clicks": 0, "pos_num": 0.0, "pos_den": 0}


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows):,} rows -> {path}")


def classify_page(url: str) -> str:
    u = (url or "").lower()
    if re.search(r"^https?://(www\.)?dtfprinterusa\.com/?$", u):
        return "Homepage"
    if "/collections/" in u:
        return "Collections"
    if "/products/" in u:
        if any(term in u for term in ["printer", "oven", "shaker", "heat-press"]):
            return "Equipment"
        if any(term in u for term in ["ink", "powder", "film", "cleaning", "supply"]):
            return "Supplies"
        return "Products"
    if "/blogs/" in u:
        return "Blogs"
    if "/pages/" in u:
        if any(term in u for term in ["stafford", "houston", "texas", "tx", "near-me"]):
            return "Local Pages"
        return "Pages"
    return "Others"


def read_ahrefs_keywords():
    if not AHREFS_KEYWORDS_FILE.exists():
        raise FileNotFoundError(f"Missing Ahrefs keyword file: {AHREFS_KEYWORDS_FILE}")
    text = AHREFS_KEYWORDS_FILE.read_text(encoding="utf-16")
    sample = text[:2048]
    dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    keywords = []
    for row in reader:
        kw = (row.get("Keyword") or "").strip().lower()
        if kw and kw not in keywords:
            keywords.append(kw)
    return keywords


def export_main_gsc(svc):
    trend_rows = []
    page_month_rows = []
    page_totals = defaultdict(metric_bucket)
    type_month_totals = defaultdict(metric_bucket)

    for year, month in months_between(TREND_START, TREND_END):
        start, end = month_dates(year, month)
        label = month_label(year, month)
        ym = f"{year}-{month:02d}"
        print(f"Main GSC: {label}")

        site_rows = query_gsc(svc, start, end)
        site = metric_bucket()
        if site_rows:
            add_metrics(site, site_rows[0])
        trend_rows.append(
            {
                "month": label,
                "year_month": ym,
                "clicks": site["clicks"],
                "impressions": site["impressions"],
                "ctr_pct": ctr_pct(site["clicks"], site["impressions"]),
                "avg_position": weighted_position(site),
            }
        )

        for row in query_gsc(svc, start, end, ["page"]):
            page = row["keys"][0]
            page_type = classify_page(page)
            total = metric_bucket()
            add_metrics(total, row)
            out = {
                "month": label,
                "year_month": ym,
                "page_type": page_type,
                "page": page,
                "clicks": total["clicks"],
                "impressions": total["impressions"],
                "ctr_pct": ctr_pct(total["clicks"], total["impressions"]),
                "avg_position": weighted_position(total),
            }
            page_month_rows.append(out)
            add_metrics(page_totals[(page, page_type)], row)
            add_metrics(type_month_totals[(ym, label, page_type)], row)

    page_rows = []
    for (page, page_type), total in page_totals.items():
        page_rows.append(
            {
                "page": page,
                "page_type": page_type,
                "clicks": total["clicks"],
                "impressions": total["impressions"],
                "ctr_pct": ctr_pct(total["clicks"], total["impressions"]),
                "avg_position": weighted_position(total),
            }
        )
    page_rows.sort(key=lambda row: (-row["clicks"], -row["impressions"]))

    type_rows = []
    for (ym, label, page_type), total in sorted(type_month_totals.items()):
        type_rows.append(
            {
                "month": label,
                "year_month": ym,
                "page_type": page_type,
                "clicks": total["clicks"],
                "impressions": total["impressions"],
                "ctr_pct": ctr_pct(total["clicks"], total["impressions"]),
                "avg_position": weighted_position(total),
            }
        )

    start, end = month_dates(*TREND_START)
    final_start, final_end = month_dates(*TREND_END)
    query_totals = defaultdict(metric_bucket)
    print("Main GSC: full-period queries")
    for row in query_gsc(svc, start, final_end, ["query"]):
        add_metrics(query_totals[row["keys"][0]], row)
    query_rows = []
    for keyword, total in query_totals.items():
        query_rows.append(
            {
                "keyword": keyword,
                "clicks": total["clicks"],
                "impressions": total["impressions"],
                "ctr_pct": ctr_pct(total["clicks"], total["impressions"]),
                "avg_position": weighted_position(total),
            }
        )
    query_rows.sort(key=lambda row: (-row["clicks"], -row["impressions"]))

    write_csv(DATA_DIR / "gsc-trend.csv", ["month", "year_month", "clicks", "impressions", "ctr_pct", "avg_position"], trend_rows)
    write_csv(DATA_DIR / "gsc-pages-monthly.csv", ["month", "year_month", "page_type", "page", "clicks", "impressions", "ctr_pct", "avg_position"], page_month_rows)
    write_csv(DATA_DIR / "gsc-pages.csv", ["page", "page_type", "clicks", "impressions", "ctr_pct", "avg_position"], page_rows)
    write_csv(DATA_DIR / "gsc-by-pagetype.csv", ["month", "year_month", "page_type", "clicks", "impressions", "ctr_pct", "avg_position"], type_rows)
    write_csv(DATA_DIR / "gsc-queries.csv", ["keyword", "clicks", "impressions", "ctr_pct", "avg_position"], query_rows)

    current = trend_rows[-1]
    previous = trend_rows[-2]
    kpis = [
        {"label": "Impressions", "value": current["impressions"], "delta": "", "direction": "", "sub": f"{current['month']} GSC impressions"},
        {"label": "Clicks", "value": current["clicks"], "delta": "", "direction": "", "sub": f"{current['month']} GSC clicks"},
        {"label": "CTR", "value": current["ctr_pct"], "delta": "", "direction": "", "sub": f"{current['month']} average CTR"},
        {"label": "Avg. Position", "value": current["avg_position"], "delta": "", "direction": "", "sub": f"{current['month']} average position"},
    ]
    write_csv(DATA_DIR / "gsc-kpis.csv", ["label", "value", "delta", "direction", "sub"], kpis)


def export_keyword_monthly(svc, target_keywords):
    target_set = set(target_keywords)
    rows_by_query = {
        kw: {"query": kw}
        for kw in target_keywords
    }
    month_fields = []

    for year, month in months_between(KEYWORD_START, KEYWORD_END):
        prefix = month_key(year, month)
        month_fields.extend([f"{prefix}_imp", f"{prefix}_clicks", f"{prefix}_pos"])
        for record in rows_by_query.values():
            record[f"{prefix}_imp"] = 0
            record[f"{prefix}_clicks"] = 0
            record[f"{prefix}_pos"] = ""

        start, end = month_dates(year, month)
        print(f"Keyword monthly: {prefix}")
        rows = query_gsc(svc, start, end, ["query"])
        for row in rows:
            query = row["keys"][0].strip().lower()
            if query not in target_set:
                continue
            impressions = int(row.get("impressions", 0))
            clicks = int(row.get("clicks", 0))
            rows_by_query[query][f"{prefix}_imp"] = impressions
            rows_by_query[query][f"{prefix}_clicks"] = clicks
            rows_by_query[query][f"{prefix}_pos"] = round(float(row.get("position", 0)), 2)

    rows = list(rows_by_query.values())
    rows.sort(key=lambda r: sum(int(r.get(f, 0) or 0) for f in month_fields if f.endswith("_imp")), reverse=True)
    write_csv(DATA_DIR / "gsc-keywords-monthly.csv", ["query", *month_fields], rows)


def classify_variant(query: str) -> str | None:
    q = query.lower()
    if re.search(r"\b(cheap|sale|price|prices|pricing|cost|discount|coupon|affordable|deal|deals)\b", q):
        return "pricing"
    if re.search(r"\b(near me|local|stafford|houston|texas|tx|sugar land|katy|missouri city|richmond)\b", q):
        return "local variants"
    if re.search(r"\b(printer|printers|machine|machines|oven|shaker|heat press|press)\b", q):
        return "equipment"
    if re.search(r"\b(ink|powder|film|roll|sheet|sheets|supplies|supply|cleaning|printhead|parts)\b", q):
        return "supplies"
    if re.search(r"\b(wholesale|bulk|supplier|vendor|b2b|business)\b", q):
        return "wholesale"
    if re.search(r"\b(what is|what are|what does|how to|meaning|vs|versus|guide|setup|tutorial|best)\b", q):
        return "education / how-to"
    if "uv dtf" in q:
        return "uv dtf"
    if re.search(r"\b(dtf printing|dtf print|dtf transfer|dtf transfers|dtf)\b", q):
        return "dtf printing"
    return None


def export_keyword_variants(svc, target_keywords):
    target_set = set(target_keywords)
    year, month = VARIANT_MONTH
    start, end = month_dates(year, month)
    print(f"Keyword variants: {start} to {end}")
    exact_rows = []
    variant_rows = []
    seen_variants = set()
    for row in query_gsc(svc, start, end, ["query", "page"]):
        query, page = row["keys"][0].strip().lower(), row["keys"][1]
        csv_row = {
            "query": query,
            "page": page,
            "clicks": int(row.get("clicks", 0)),
            "impressions": int(row.get("impressions", 0)),
            "ctr": f"{float(row.get('ctr', 0)):.2%}",
            "position": round(float(row.get("position", 0)), 1),
            "match_type": "",
            "matched_seed": "",
        }
        if query in target_set:
            csv_row["match_type"] = "exact"
            exact_rows.append(csv_row)
        else:
            category = classify_variant(query)
            if category and query not in seen_variants:
                seen_variants.add(query)
                csv_row["match_type"] = "variant"
                csv_row["matched_seed"] = category
                variant_rows.append(csv_row)

    exact_rows.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    variant_rows.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    fields = ["query", "page", "clicks", "impressions", "ctr", "position", "match_type", "matched_seed"]
    write_csv(DATA_DIR / "gsc-keywords-exact.csv", fields, exact_rows)
    write_csv(DATA_DIR / "gsc-keyword-variants.csv", fields, variant_rows)


def main():
    print(f"Reading Ahrefs keywords from {AHREFS_KEYWORDS_FILE}")
    target_keywords = read_ahrefs_keywords()
    print(f"Loaded {len(target_keywords):,} Ahrefs keywords")
    svc = service()
    export_main_gsc(svc)
    export_keyword_monthly(svc, target_keywords)
    export_keyword_variants(svc, target_keywords)
    print("Done.")


if __name__ == "__main__":
    main()
