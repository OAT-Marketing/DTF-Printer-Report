# aisearch.html CSV schema

## aisearch-ga4-trend.csv
Monthly GA4 AI traffic totals.

Columns: `month,sessions,engaged_sessions,total_users,new_users,views`

Example: `Apr 2026,132,110,125,49,203`

## aisearch-llm-sources.csv
Latest-month GA4 AI traffic by source.

Columns: `source,sessions,engaged_sessions,total_users,new_users,views,share_pct,engaged_rate`

Example: `chatgpt.com,114,92,107,42,172,86.4,80.7`

## aisearch-ga4-pages.csv
Latest-month GA4 AI landing pages.

Columns: `page,sessions,engaged_sessions,total_users,new_users,views`

Example: `/,17,14,17,16,35`

## aisearch-bing-trend.csv
Monthly Bing AI / Copilot citation totals.

Columns: `month,citations,cited_pages`

Example: `Apr 2026,2067,10`

## aisearch-bing-pages.csv
Bing AI / Copilot cited pages.

Columns: `page,citations`

Example: `https://dtfjersey.com/,1635`

## aisearch-bing-queries.csv
Bing AI / Copilot grounding queries.

Columns: `query,citations`

Example: `dtf transfers elmwood park nj,226`
