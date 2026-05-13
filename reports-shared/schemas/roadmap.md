# roadmap.html

## data/roadmap-kpis.csv (KPI grid at top)
Columns: `label,value,delta,direction,sub`
Example:
```
label,value,delta,direction,sub
Sessions,12450,+8%,up,vs prior period
New backlinks,42,+12,up,April 2026
Top-3 keywords,18,-2,down,4 dropped
```

## data/roadmap-phases.csv (3-column phase cards)
Columns: `header,phase,bullets`
- `phase`: `p1` (red), `p2` (orange), `p3` (blue)
- `bullets`: pipe-separated list `Item one|Item two|Item three`

Example:
```
header,phase,bullets
"Phase 1 · Foundation (Apr–May)",p1,"Fix 4xx errors on local pages|Rewrite weak meta titles|Submit Bing sitemap"
"Phase 2 · Growth (Jun–Aug)",p2,"Publish 12 cluster articles|Build 20 referring domains|Optimise top 5 collections"
"Phase 3 · Scale (Sep–Dec)",p3,"Launch comparison pages|Outreach for tier-1 backlinks|Refresh existing top-10 posts"
```
