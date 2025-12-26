# Migration Flow Tool

*"Where are people moving?" — County-to-county migration patterns using IRS data.*

---

## Quick Reference

| Doc | Purpose |
|-----|---------|
| `spec.md` | Full requirements, design decisions, user flow |
| `data/scripts/process_migration_data.py` | Reprocess raw data if needed |

---

## Status

**Phase 1 (Data):** ✅ Complete
**Phase 2 (Web App):** ✅ Complete — ready to test locally
**Phase 3 (Deploy):** ⏳ Next step — deploy to Vercel

---

## Project Structure

```
Migration Flow Tool/
├── CLAUDE.md              ← This file
├── spec.md                ← Full specification
├── data/
│   ├── raw/               ← IRS source files
│   ├── processed/
│   │   ├── migration_data.json   (4.9 MB)
│   │   └── county_list.json      (173 KB)
│   └── scripts/
│       └── process_migration_data.py
└── app/                   ← Web application
    ├── index.html
    ├── styles.css
    ├── app.js
    └── data/
        ├── migration_data.json
        └── county_list.json
```

---

## Known Issues

- **Connecticut excluded** — IRS uses planning regions, not counties. Note in app methodology section.
- **Suppressed data** — Small flows (<10 returns) filtered out for privacy.

---

## Data Notes

- **Source:** IRS SOI Migration Data 2021-2022
- **Households** = tax returns filed
- **AGI** = Adjusted Gross Income (in dollars, already converted from thousands)
- **2,730 counties** in dataset

---

*Updated: December 26, 2025*
