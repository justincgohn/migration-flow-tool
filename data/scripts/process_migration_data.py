"""
Process IRS SOI Migration Data into JSON for web app.

Reads:
- countyinflow2122.csv (where people came FROM)
- countyoutflow2122.csv (where people went TO)
- fips_county_lookup.txt (FIPS code to county name mapping)

Outputs:
- Single JSON file with all county data, keyed by FIPS code
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"

# Summary row STATE codes to filter out
# 96-99 in STATE FIPS = various aggregates (foreign, same state, etc.)
# NOTE: Only check STATE codes, not county codes!
# Counties like Palm Beach FL (12_099), Marion IN (18_097), etc. use 96-99 as valid county FIPS
# Summary rows are also filtered by name pattern ("Other flows", "Total Migration")
SUMMARY_STATE_CODES = {96, 97, 98, 99}


def load_fips_lookup():
    """Load FIPS code to county name mapping."""
    lookup = {}
    fips_file = RAW_DIR / "fips_county_lookup.txt"

    with open(fips_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            state_fips = row['STATEFP']
            county_fips = row['COUNTYFP']
            key = f"{state_fips}_{county_fips}"
            lookup[key] = {
                'state': row['STATE'],
                'county': row['COUNTYNAME'],
                'state_fips': state_fips,
                'county_fips': county_fips
            }

    print(f"Loaded {len(lookup)} county FIPS codes")
    return lookup


def get_county_name(fips_lookup, state_fips, county_fips):
    """Get county name from FIPS codes."""
    # Pad with leading zeros
    state_fips = str(state_fips).zfill(2)
    county_fips = str(county_fips).zfill(3)
    key = f"{state_fips}_{county_fips}"

    if key in fips_lookup:
        info = fips_lookup[key]
        return f"{info['county']}, {info['state']}"
    return None


def process_outflow(fips_lookup):
    """Process outflow data (where people are going TO from each county)."""
    outflow_file = RAW_DIR / "countyoutflow2122.csv"
    county_data = defaultdict(lambda: {'outflows': [], 'total_out': 0, 'total_out_agi': 0})

    with open(outflow_file, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origin_state = int(row['y1_statefips'])
            origin_county = int(row['y1_countyfips'])
            dest_state = int(row['y2_statefips'])
            dest_county = int(row['y2_countyfips'])

            # Skip summary rows (only check STATE codes, not county codes)
            if dest_state in SUMMARY_STATE_CODES or origin_state in SUMMARY_STATE_CODES:
                continue

            # Skip non-migrant rows (same county)
            if origin_state == dest_state and origin_county == dest_county:
                continue

            # Get counts (handle suppressed data marked as -1)
            households = int(row['n1'])
            people = int(row['n2'])
            agi = int(row['agi'])

            if households <= 0:
                continue

            # Build origin key
            origin_key = f"{str(origin_state).zfill(2)}_{str(origin_county).zfill(3)}"

            # Get destination name from the data (it's included)
            dest_name = f"{row['y2_countyname']}, {row['y2_state']}"

            # Skip summary rows by name pattern
            if 'Other flows' in dest_name or 'Total Migration' in dest_name:
                continue

            # Calculate average AGI (AGI is in thousands)
            avg_agi = round((agi * 1000) / households) if households > 0 else 0

            county_data[origin_key]['outflows'].append({
                'destination': dest_name,
                'dest_fips': f"{str(dest_state).zfill(2)}_{str(dest_county).zfill(3)}",
                'households': households,
                'people': people,
                'total_agi': agi * 1000,
                'avg_agi': avg_agi
            })
            county_data[origin_key]['total_out'] += households
            county_data[origin_key]['total_out_agi'] += agi * 1000

    # Sort outflows by household count and keep top 20
    for key in county_data:
        county_data[key]['outflows'].sort(key=lambda x: x['households'], reverse=True)
        county_data[key]['outflows'] = county_data[key]['outflows'][:20]

        # Calculate average AGI for all outflows
        total_out = county_data[key]['total_out']
        if total_out > 0:
            county_data[key]['avg_out_agi'] = round(county_data[key]['total_out_agi'] / total_out)

    print(f"Processed outflow data for {len(county_data)} counties")
    return county_data


def process_inflow(fips_lookup):
    """Process inflow data (where people are coming FROM to each county)."""
    inflow_file = RAW_DIR / "countyinflow2122.csv"
    county_data = defaultdict(lambda: {'inflows': [], 'total_in': 0, 'total_in_agi': 0})

    with open(inflow_file, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origin_state = int(row['y1_statefips'])
            origin_county = int(row['y1_countyfips'])
            dest_state = int(row['y2_statefips'])
            dest_county = int(row['y2_countyfips'])

            # Skip summary rows (only check STATE codes, not county codes)
            if origin_state in SUMMARY_STATE_CODES or dest_state in SUMMARY_STATE_CODES:
                continue

            # Skip non-migrant rows (same county)
            if origin_state == dest_state and origin_county == dest_county:
                continue

            # Get counts
            households = int(row['n1'])
            people = int(row['n2'])
            agi = int(row['agi'])

            if households <= 0:
                continue

            # Build destination key (the county receiving people)
            dest_key = f"{str(dest_state).zfill(2)}_{str(dest_county).zfill(3)}"

            # Get origin name directly from the data (it's included!)
            origin_name = f"{row['y1_countyname']}, {row['y1_state']}"

            # Skip summary rows by name pattern
            if 'Other flows' in origin_name or 'Total Migration' in origin_name:
                continue

            # Calculate average AGI
            avg_agi = round((agi * 1000) / households) if households > 0 else 0

            county_data[dest_key]['inflows'].append({
                'origin': origin_name,
                'origin_fips': f"{str(origin_state).zfill(2)}_{str(origin_county).zfill(3)}",
                'households': households,
                'people': people,
                'total_agi': agi * 1000,
                'avg_agi': avg_agi
            })
            county_data[dest_key]['total_in'] += households
            county_data[dest_key]['total_in_agi'] += agi * 1000

    # Sort inflows by household count and keep top 20
    for key in county_data:
        county_data[key]['inflows'].sort(key=lambda x: x['households'], reverse=True)
        county_data[key]['inflows'] = county_data[key]['inflows'][:20]

        # Calculate average AGI for all inflows
        total_in = county_data[key]['total_in']
        if total_in > 0:
            county_data[key]['avg_in_agi'] = round(county_data[key]['total_in_agi'] / total_in)

    print(f"Processed inflow data for {len(county_data)} counties")
    return county_data


def merge_and_output(fips_lookup, outflow_data, inflow_data):
    """Merge inflow and outflow data and output JSON."""
    # Get all unique county keys
    all_keys = set(outflow_data.keys()) | set(inflow_data.keys())

    final_data = {}

    for key in all_keys:
        # Get county info
        county_info = fips_lookup.get(key, {})
        if not county_info:
            continue

        county_name = f"{county_info['county']}, {county_info['state']}"

        out_data = outflow_data.get(key, {'outflows': [], 'total_out': 0, 'avg_out_agi': 0})
        in_data = inflow_data.get(key, {'inflows': [], 'total_in': 0, 'avg_in_agi': 0})

        net_migration = in_data.get('total_in', 0) - out_data.get('total_out', 0)

        final_data[key] = {
            'name': county_name,
            'state': county_info['state'],
            'county': county_info['county'],
            'fips': key,
            'year': '2021-2022',
            'outflows': out_data.get('outflows', [])[:10],  # Top 10 for display
            'inflows': in_data.get('inflows', [])[:10],     # Top 10 for display
            'summary': {
                'total_leaving': out_data.get('total_out', 0),
                'total_arriving': in_data.get('total_in', 0),
                'net_migration': net_migration,
                'avg_agi_leaving': out_data.get('avg_out_agi', 0),
                'avg_agi_arriving': in_data.get('avg_in_agi', 0)
            }
        }

    # Also create a simple lookup list for search
    county_list = [
        {'fips': key, 'name': data['name'], 'state': data['state']}
        for key, data in final_data.items()
    ]
    county_list.sort(key=lambda x: x['name'])

    # Write main data file
    PROCESSED_DIR.mkdir(exist_ok=True)

    main_file = PROCESSED_DIR / "migration_data.json"
    with open(main_file, 'w') as f:
        json.dump(final_data, f)
    print(f"Wrote main data file: {main_file} ({main_file.stat().st_size / 1024 / 1024:.1f} MB)")

    # Write county list for autocomplete
    list_file = PROCESSED_DIR / "county_list.json"
    with open(list_file, 'w') as f:
        json.dump(county_list, f)
    print(f"Wrote county list: {list_file} ({len(county_list)} counties)")

    return final_data


def print_sample(data, county_fips="42_101"):
    """Print sample output for a county (default: Philadelphia)."""
    if county_fips not in data:
        print(f"County {county_fips} not found")
        return

    county = data[county_fips]
    print("\n" + "="*60)
    print(f"SAMPLE OUTPUT: {county['name']}")
    print("="*60)

    print(f"\nWHERE THEY'RE GOING ({county['year']})")
    for i, flow in enumerate(county['outflows'][:5], 1):
        avg_agi = f"${flow['avg_agi']:,}" if flow['avg_agi'] > 0 else "N/A"
        print(f"  {i}. {flow['destination']} — {flow['households']:,} households ({avg_agi} avg AGI)")

    print(f"\nWHERE THEY'RE COMING FROM ({county['year']})")
    for i, flow in enumerate(county['inflows'][:5], 1):
        avg_agi = f"${flow['avg_agi']:,}" if flow['avg_agi'] > 0 else "N/A"
        print(f"  {i}. {flow['origin']} — {flow['households']:,} households ({avg_agi} avg AGI)")

    summary = county['summary']
    print(f"\nSUMMARY")
    print(f"  Total leaving: {summary['total_leaving']:,} households")
    print(f"  Total arriving: {summary['total_arriving']:,} households")
    print(f"  Net migration: {summary['net_migration']:+,} households")
    print(f"  Avg AGI leaving: ${summary['avg_agi_leaving']:,}")
    print(f"  Avg AGI arriving: ${summary['avg_agi_arriving']:,}")
    print()


if __name__ == "__main__":
    print("Loading FIPS lookup table...")
    fips_lookup = load_fips_lookup()

    print("\nProcessing outflow data...")
    outflow_data = process_outflow(fips_lookup)

    print("\nProcessing inflow data...")
    inflow_data = process_inflow(fips_lookup)

    print("\nMerging and outputting JSON...")
    final_data = merge_and_output(fips_lookup, outflow_data, inflow_data)

    # Print sample for Philadelphia
    print_sample(final_data, "42_101")

    print("Done!")
