# CSV Schemas

One CSV file per data block. Drop into `<client>/reports/data/` with the exact filename listed.

## Conventions

- **Encoding**: UTF-8, comma-separated. Quote fields containing commas or newlines (`"like, this"`).
- **First row**: column headers (must match the schema exactly).
- **Numbers**: plain numbers are fine (`1234` or `1.2`). String values like `"1.2K"`, `"82%"` are allowed in display-only columns (`value`, `delta`).
- **Empty cells**: leave blank, do not write `null` or `NA`.
- **`direction`** column (for KPIs): `up` (green), `down` (red), or blank.
- **`severity`** / **`priority`** column (for tables with `badge-col`): `high`, `medium`, `low`. Custom values render as a neutral pill.
- **Bullets in a single cell**: separate with `|` (used by `<cards-grid>` `bullets` column).

## Per-page CSV files

See individual schema files in this directory:

- `roadmap.md`
- `gsc.md`
- `ga4.md`
- `aisearch.md`
- `keywords.md`
- `audit.md`
- `backlinks.md`
- `brightlocal.md`
- `bing.md`
- `shopify.md`

`index.html` is config-only — no CSV needed.
