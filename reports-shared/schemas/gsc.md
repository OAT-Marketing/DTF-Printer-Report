# gsc.html — Google Search Console

## data/gsc-kpis.csv
Columns: `label,value,delta,direction,sub`
```
label,value,delta,direction,sub
Clicks,18432,+14%,up,Apr 2026
Impressions,512000,+9%,up,Apr 2026
CTR,3.6%,+0.4%,up,
Avg position,18.2,-2.1,up,lower is better
```

## data/gsc-trend.csv (line chart: clicks/impressions over time)
Columns: `month,clicks,impressions,ctr,position`
```
month,clicks,impressions,ctr,position
2025-09,9200,310000,2.97,22.4
2025-10,10100,340000,2.97,21.8
...
```

## data/gsc-pages.csv (top-pages table)
Columns: `page,clicks,impressions,ctr,position`
Same shape as existing DTF Dallas gsc_pages.csv. Sort by clicks descending. Top 100 rows recommended.
