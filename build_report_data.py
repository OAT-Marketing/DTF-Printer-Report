
"""
Normalize DTFPrinterUSA raw exports into the report-ready CSV files.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def read_csv(path, encoding="utf-8-sig"):
    with (DATA / path).open(newline="", encoding=encoding) as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        return list(csv.DictReader(handle, dialect=dialect))


def write_csv(path, fields, rows):
    with (DATA / path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows):,} rows -> {path}")


def n(value):
    text = str(value or "").replace(",", "").replace("%", "").strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def month_sort(label):
    for fmt in ("%b %Y", "%B %Y", "%Y-%m-%d", "%m/%d/%Y %I:%M:%S %p"):
        try:
            return datetime.strptime(str(label).strip(), fmt)
        except ValueError:
            pass
    return datetime.max


def month_label_from_date(value):
    value = str(value or "").strip()
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d", "%b %Y", "%B %Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%b %Y")
        except ValueError:
            pass
    return value


def add_metrics(bucket, row, views_key="Views"):
    bucket["total_users"] += n(row.get("Total users"))
    bucket["sessions"] += n(row.get("Sessions"))
    bucket["engaged_sessions"] += n(row.get("Engaged sessions"))
    bucket["new_users"] += n(row.get("New users"))
    bucket["views"] += n(row.get(views_key))


def clean_channel(value):
    value = str(value or "").strip()
    return value or "Unassigned"


def build_ga4():
    rows = read_csv("dtfprinterusa-ga4-yearly.csv")
    monthly = defaultdict(lambda: defaultdict(float))
    channels = defaultdict(lambda: defaultdict(float))
    landing = defaultdict(lambda: defaultdict(float))
    for row in rows:
        month = row.get("Date (Year Month)", "").strip()
        page = row.get("Page path and screen class", "").strip() or "/"
        channel = clean_channel(row.get("Session default channel group"))
        add_metrics(monthly[month], row)
        add_metrics(channels[(channel, month)], row)
        add_metrics(landing[(page, channel, month)], row)
    total_sessions_by_month = defaultdict(float)
    for (channel, month), vals in channels.items():
        total_sessions_by_month[month] += vals["sessions"]
    monthly_rows = [{"month": month, **{k: int(v) for k, v in vals.items()}} for month, vals in sorted(monthly.items(), key=lambda item: month_sort(item[0]))]
    channel_rows = []
    for (channel, month), vals in sorted(channels.items(), key=lambda item: (month_sort(item[0][1]), item[0][0])):
        sessions = vals["sessions"]
        total = total_sessions_by_month[month]
        channel_rows.append({"channel": channel, "month": month, "total_users": int(vals["total_users"]), "sessions": int(sessions), "engaged_sessions": int(vals["engaged_sessions"]), "new_users": int(vals["new_users"]), "views": int(vals["views"]), "share_pct": round(sessions / total * 100, 2) if total else 0})
    landing_rows = [{"page": page, "channel": channel, "month": month, "sessions": int(vals["sessions"]), "total_users": int(vals["total_users"]), "engaged_sessions": int(vals["engaged_sessions"]), "new_users": int(vals["new_users"]), "views": int(vals["views"])} for (page, channel, month), vals in sorted(landing.items(), key=lambda item: (month_sort(item[0][2]), -item[1]["sessions"]))]
    write_csv("ga4-monthly.csv", ["month", "total_users", "sessions", "engaged_sessions", "new_users", "views"], monthly_rows)
    write_csv("ga4-channels.csv", ["channel", "month", "total_users", "sessions", "engaged_sessions", "new_users", "views", "share_pct"], channel_rows)
    write_csv("ga4-landing.csv", ["page", "channel", "month", "sessions", "total_users", "engaged_sessions", "new_users", "views"], landing_rows)


def build_ai_ga4():
    rows = read_csv("dtfprinterusa-ga4-aisearch-page-breakdown.csv")
    trend = defaultdict(lambda: defaultdict(float))
    sources = defaultdict(lambda: defaultdict(float))
    pages = defaultdict(lambda: defaultdict(float))
    for row in rows:
        month = row.get("Date (Year Month)", "").strip()
        source = row.get("Session source", "").strip() or "AI source"
        page = row.get("Page path and screen class", "").strip() or "/"
        add_metrics(trend[month], row)
        add_metrics(sources[source], row)
        if month == "Apr 2026":
            add_metrics(pages[page], row)
    total_sessions = sum(vals["sessions"] for vals in sources.values())
    trend_rows = [{"month": month, **{k: int(v) for k, v in vals.items()}} for month, vals in sorted(trend.items(), key=lambda item: month_sort(item[0]))]
    source_rows = []
    for source, vals in sorted(sources.items(), key=lambda item: -item[1]["sessions"]):
        sessions = vals["sessions"]
        source_rows.append({"source": source, "sessions": int(sessions), "engaged_sessions": int(vals["engaged_sessions"]), "total_users": int(vals["total_users"]), "new_users": int(vals["new_users"]), "views": int(vals["views"]), "share_pct": round(sessions / total_sessions * 100, 2) if total_sessions else 0, "engaged_rate": round(vals["engaged_sessions"] / sessions * 100, 2) if sessions else 0})
    page_rows = [{"page": page, **{k: int(v) for k, v in vals.items()}} for page, vals in sorted(pages.items(), key=lambda item: -item[1]["sessions"])]
    write_csv("aisearch-ga4-trend.csv", ["month", "sessions", "engaged_sessions", "total_users", "new_users", "views"], trend_rows)
    write_csv("aisearch-llm-sources.csv", ["source", "sessions", "engaged_sessions", "total_users", "new_users", "views", "share_pct", "engaged_rate"], source_rows)
    write_csv("aisearch-ga4-pages.csv", ["page", "sessions", "engaged_sessions", "total_users", "new_users", "views"], page_rows)


def build_bing():
    yearly = read_csv("dtfprinterusa-bing-yearly.csv")
    trend = defaultdict(lambda: {"impressions": 0.0, "clicks": 0.0})
    for row in yearly:
        month = month_label_from_date(row.get("Date"))
        trend[month]["impressions"] += n(row.get("Impressions"))
        trend[month]["clicks"] += n(row.get("Clicks"))
    trend_rows = []
    for month, vals in sorted(trend.items(), key=lambda item: month_sort(item[0])):
        impressions = vals["impressions"]
        clicks = vals["clicks"]
        trend_rows.append({"month": month, "impressions": int(impressions), "clicks": int(clicks), "ctr": round(clicks / impressions * 100, 2) if impressions else 0, "position": ""})
    def detail_rows(source, label_field):
        out = []
        for row in read_csv(source):
            impressions = n(row.get("Impressions"))
            clicks = n(row.get("Clicks"))
            out.append({label_field: row.get("Keyword") or row.get("Page") or "", "impressions": int(impressions), "clicks": int(clicks), "ctr": row.get("CTR") or (round(clicks / impressions * 100, 2) if impressions else 0), "position": round(n(row.get("Avg. Position")), 2)})
        return sorted(out, key=lambda r: (-r["clicks"], -r["impressions"]))
    write_csv("bing-trend.csv", ["month", "impressions", "clicks", "ctr", "position"], trend_rows)
    write_csv("bing-queries.csv", ["keyword", "impressions", "clicks", "ctr", "position"], detail_rows("dtfprinterusa-queries-april2026.csv", "keyword"))
    write_csv("bing-pages.csv", ["page", "impressions", "clicks", "ctr", "position"], detail_rows("dtfprinterusa-pages-april2026.csv", "page"))


def build_ai_bing():
    trend = defaultdict(lambda: {"citations": 0.0, "cited_pages": 0.0})
    for row in read_csv("dtfprinterusa-aisearch-trend.csv"):
        month = month_label_from_date(row.get("Date"))
        trend[month]["citations"] += n(row.get("Citations"))
        trend[month]["cited_pages"] = max(trend[month]["cited_pages"], n(row.get("Cited Pages")))
    trend_rows = [{"month": month, "citations": int(vals["citations"]), "cited_pages": int(vals["cited_pages"])} for month, vals in sorted(trend.items(), key=lambda item: month_sort(item[0]))]
    pages = [{"page": row.get("Page", ""), "citations": int(n(row.get("Citations")))} for row in read_csv("dtfprinterusa-aisearch-pages-april2026.csv")]
    queries = [{"query": row.get("Grounding Query", ""), "citations": int(n(row.get("Citations")))} for row in read_csv("dtfprinterusa-aisearch-queries-april2026.csv")]
    write_csv("aisearch-bing-trend.csv", ["month", "citations", "cited_pages"], trend_rows)
    write_csv("aisearch-bing-pages.csv", ["page", "citations"], sorted(pages, key=lambda r: -r["citations"]))
    write_csv("aisearch-bing-queries.csv", ["query", "citations"], sorted(queries, key=lambda r: -r["citations"]))


def build_audit():
    severity_map = {"Error": "Error", "Warning": "Warning", "Notice": "Notice"}
    rows = [{"issue": row.get("Issue", "").strip(), "count": int(n(row.get("Pages affected"))), "severity": severity_map.get(row.get("Type", "").strip(), row.get("Type", "").strip() or "Notice")} for row in read_csv("dtfprinterusa-bing-site-scan-may5th.csv")]
    write_csv("audit-issues.csv", ["issue", "count", "severity"], rows)


def build_shopify():
    raw = read_csv("shopify-analytics-data.csv")
    monthly = defaultdict(lambda: {"orders": 0.0, "cvr_sum": 0.0, "rows": 0})
    channels = defaultdict(lambda: {"orders": 0.0, "cvr_sum": 0.0, "rows": 0})
    for row in raw:
        month = month_label_from_date(row.get("Month"))
        channel = clean_channel(row.get("Referring channel"))
        orders = n(row.get("Orders (last click)"))
        cvr = n(row.get("Conversion rate")) * 100
        monthly[month]["orders"] += orders
        monthly[month]["cvr_sum"] += cvr
        monthly[month]["rows"] += 1
        channels[(month, channel)]["orders"] += orders
        channels[(month, channel)]["cvr_sum"] += cvr
        channels[(month, channel)]["rows"] += 1
    monthly_rows = [{"month": month, "orders": int(vals["orders"]), "conversion_rate": round(vals["cvr_sum"] / vals["rows"], 2) if vals["rows"] else 0} for month, vals in sorted(monthly.items(), key=lambda item: month_sort(item[0]))]
    channel_rows = [{"month": month, "channel": channel, "orders": int(vals["orders"]), "conversion_rate": round(vals["cvr_sum"] / vals["rows"], 2) if vals["rows"] else 0} for (month, channel), vals in sorted(channels.items(), key=lambda item: (month_sort(item[0][0]), item[0][1]))]
    by_channel = defaultdict(dict)
    for row in channel_rows:
        by_channel[row["channel"]][row["month"]] = row
    order_rows = []
    cvr_rows = []
    for channel, vals in sorted(by_channel.items()):
        apr_orders = vals.get("Apr 2026", {}).get("orders", 0)
        mar_orders = vals.get("Mar 2026", {}).get("orders", 0)
        apr_cvr = vals.get("Apr 2026", {}).get("conversion_rate", 0)
        mar_cvr = vals.get("Mar 2026", {}).get("conversion_rate", 0)
        order_rows.append({"channel": channel, "apr_orders": apr_orders, "mar_orders": mar_orders, "mom_pct": "New" if not mar_orders and apr_orders else round((apr_orders - mar_orders) / mar_orders * 100, 1) if mar_orders else 0})
        cvr_rows.append({"channel": channel, "apr_cvr": apr_cvr, "mar_cvr": mar_cvr, "mom_delta_pp": round(apr_cvr - mar_cvr, 2)})
    write_csv("shopify-monthly.csv", ["month", "orders", "conversion_rate"], monthly_rows)
    write_csv("shopify-channel-monthly.csv", ["month", "channel", "orders", "conversion_rate"], channel_rows)
    write_csv("shopify-orders-by-channel.csv", ["channel", "apr_orders", "mar_orders", "mom_pct"], order_rows)
    write_csv("shopify-cvr-by-channel.csv", ["channel", "apr_cvr", "mar_cvr", "mom_delta_pp"], cvr_rows)


def main():
    build_ga4()
    build_ai_ga4()
    build_bing()
    build_ai_bing()
    build_audit()
    build_shopify()


if __name__ == "__main__":
    main()
