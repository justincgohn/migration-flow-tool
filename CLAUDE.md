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
**Phase 2 (Web App):** ✅ Complete
**Phase 3 (Deploy):** ✅ Live on GitHub Pages

**Live URL:** https://justincgohn.github.io/migration-flow-tool/
**Repo:** https://github.com/justincgohn/migration-flow-tool

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
└── docs/                  ← Web application (GitHub Pages serves from here)
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
- **2,793 counties** in dataset

---

*Updated: December 26, 2025*
