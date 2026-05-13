# index.html schema

The cover page does not consume report CSV files. It reads client metadata from `DTFJersey/reports/config.json` through `reports-shared/assets/config-loader.js`.

Required config keys: `client_name`, `report_period`, `report_date`, `logo`, `primary_color`.

Example config:

```json
{ "client_name": "DTF Jersey", "report_date": "May 2026", "logo": "../../reports-shared/assets/logo-oat-white.png", "primary_color": "#F28C28" }
```
