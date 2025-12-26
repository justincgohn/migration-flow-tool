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

## Change Log

### December 26, 2025 — Bug fix: Missing counties (FIPS 057-059)

**Issue:** User reported Orange County, CA not appearing in search.

**Root cause:** `process_migration_data.py` had `SUMMARY_CODES = {57, 58, 59, 96, 97, 98, 99}` which filtered out any county with FIPS code ending in 057, 058, or 059. These codes are only summary codes at certain aggregation levels, not at the county level.

**Impact:** 63 counties were missing, including:
- Orange County, CA (06_059) — 3.2M population
- Nassau County, NY (36_059) — 1.4M population
- Fairfax County, VA (51_059) — 1.1M population
- Hillsborough County, FL (12_057) — 1.5M population

**Fix:** Removed 57, 58, 59 from `SUMMARY_CODES`. Summary rows are already filtered by name pattern ("Other flows", "Total Migration") so the FIPS-based filter was redundant.

**Result:** County count increased from 2,730 to 2,793.

---

*Updated: December 26, 2025*
