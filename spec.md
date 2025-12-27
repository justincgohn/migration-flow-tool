# Migration Flow Tool — Specification

*Generated through iterative questioning per LLM Dev Workflow*

---

## Overview

A simple web app that lets users explore county-to-county migration patterns using IRS data. User searches for a county → sees where people are moving to/from, with income data.

**Inspiration:** Name Age Calculator — simple input, surprising output, shareable result.

---

## User Flow

1. **Landing page**
   - Clean search box, prominently centered
   - 3-4 featured example counties below: "Try: Philadelphia, San Francisco, Miami, Austin"
   - Minimal design, lots of whitespace

2. **Search interaction**
   - Autocomplete as user types (2,855 counties)
   - Selecting a county navigates to results page

3. **Results page**
   - URL structure: `/county/philadelphia-pa` (shareable)
   - Display county name prominently
   - Show top 5 destinations ("Where they're going")
   - Show top 5 sources ("Where they're coming from")
   - Summary box with:
     - Net migration (households gained/lost)
     - Avg AGI leaving vs arriving
   - Data source link at bottom

4. **Navigation**
   - Easy way to search again (persistent search box or "Search another county" link)
   - Clicking a destination/source county could navigate to that county's page

---

## Design Requirements

| Aspect | Decision |
|--------|----------|
| Style | Minimal/clean, lots of whitespace |
| Typography | Simple, readable, modern sans-serif |
| Colors | Neutral palette, subtle accent for key stats |
| Mobile | Responsive, works on phone |
| Branding | "justingohn.com" in header and footer, tasteful |

---

## Data Display

### Results table (each direction)
| Rank | County | Households | Avg AGI |
|------|--------|------------|---------|
| 1 | Montgomery County, PA | 6,297 | $105,992 |
| 2 | Delaware County, PA | 4,995 | $83,771 |
| ... | ... | ... | ... |

- Show top 5 each direction
- Format numbers with commas
- Format AGI as currency

### Summary stats
- Net migration: "+2,341 households" or "-9,465 households"
- Avg AGI leaving: $87,174
- Avg AGI arriving: $72,823
- Year: 2021-2022

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Small rural county | Show available data with disclaimer: "Limited migration data available for this county" |
| County not found | Show "County not found" message with search prompt |
| Connecticut | Excluded from data (planning regions issue). Note in methodology section. |

---

## Technical Approach

| Component | Decision |
|-----------|----------|
| Frontend | Plain HTML/CSS/JS (no framework) |
| Data loading | Load full JSON on page load (~5MB) |
| Hosting | GitHub Pages |
| URL routing | Hash-based or simple path routing |
| Search | Client-side filtering of county list |

### File structure (planned)
```
app/
├── index.html
├── styles.css
├── app.js
├── data/
│   ├── migration_data.json
│   └── county_list.json
└── assets/
    └── (any images/icons)
```

---

## Content Sections

### Header
- Site title/logo area
- "justingohn.com" link

### Footer
- "Data source: IRS Statistics of Income"
- Link to methodology/about
- "justingohn.com"

### Methodology section (expandable or separate page)
- Data comes from IRS SOI Migration Data (2021-2022 tax returns)
- "Households" = tax returns filed
- "AGI" = Adjusted Gross Income
- Note: Connecticut excluded due to planning region data structure
- Link to IRS source

---

## Out of Scope (v1)

- Maps or visualizations
- Historical trends / multi-year comparison
- State-level aggregation
- Sankey diagrams
- User accounts or saved searches
- API for external access

---

## Success Criteria

- [x] User can search and find any of the 2,855 counties
- [ ] Results display correctly with formatted numbers
- [ ] URLs are shareable and work when accessed directly
- [ ] Page loads in under 3 seconds on typical connection
- [ ] Mobile responsive
- [ ] Data source clearly attributed

---

*Spec created: December 26, 2025*
