"""
analyze_session_continuity.py
=============================
Detailed audit of SPX option session continuity across 2010-2021.
Compares observed SPX option quote dates against the official NYSE/Cboe exchange trading calendar (3,021 sessions).
Computes:
1. Missing sessions by year and month
2. Unexpected sessions (e.g. weekend or holiday option records)
3. Annual and full-period missingness rates
4. Quote readtime conventions across vintages, including early closes
"""

import os
import glob
import json
import pandas as pd
import yfinance as yf

base_dir = r"Data\SPX Options Chain"
folders = [
    ('2010', 'spx_eod_2010-hixkhi'),
    ('2011', 'spx_eod_2011-mpv77a'),
    ('2012', 'spx_eod_2012-ftrobg'),
    ('2013', 'spx_eod_2013-3p7m9u'),
    ('2014', 'spx_eod_2014-4ky8n2'),
    ('2015', 'spx_eod_2015-amtjlk'),
    ('2016', 'spx_eod_2016-rctzlw'),
    ('2017', 'spx_eod_2017-xspity'),
    ('2018', 'spx_eod_2018-uqawfl'),
    ('2019', 'spx_eod_2019-chxexe'),
    ('2020', 'spx_eod_2020-wh6jt7'),
    ('2021', 'spx_eod_2021-n4uqkm'),
    ('2021', 'spx_eod_2021q3-kgzold'),
    ('2021', 'spx_eod_2021q4-r3h0dx'),
]

# 1. Official GSPC trading days (the authoritative exchange calendar)
gspc = yf.download('^GSPC', start='2010-01-01', end='2022-01-01', progress=False)
expected_dates = sorted(set(gspc.index.strftime('%Y-%m-%d')))
print(f"Total official expected exchange sessions (2010-2021): {len(expected_dates)}")

# 2. Extract observed SPX option dates and timestamps
observed_dates_by_month = {}
observed_readtimes_by_date = {}
row_counts_by_date = {}

for yr, folder in folders:
    fdir = os.path.join(base_dir, folder)
    txt_files = sorted(glob.glob(os.path.join(fdir, "*.txt")))
    for fpath in txt_files:
        month_key = os.path.basename(fpath).replace("spx_eod_", "").replace(".txt", "")
        observed_dates_by_month[month_key] = set()
        with open(fpath, 'r') as f:
            header = [h.strip().replace('[', '').replace(']', '') for h in f.readline().split(',')]
            qdate_idx = header.index('QUOTE_DATE')
            qtime_idx = header.index('QUOTE_READTIME')
            for line in f:
                parts = line.split(',')
                if len(parts) > qdate_idx:
                    qd = parts[qdate_idx].strip()
                    qt = parts[qtime_idx].strip()
                    observed_dates_by_month[month_key].add(qd)
                    if qd not in observed_readtimes_by_date:
                        observed_readtimes_by_date[qd] = set()
                        row_counts_by_date[qd] = 0
                    observed_readtimes_by_date[qd].add(qt)
                    row_counts_by_date[qd] += 1

all_observed_dates = sorted(observed_readtimes_by_date.keys())
print(f"Total observed SPX option sessions (2010-2021): {len(all_observed_dates)}")

# 3. Discrepancy analysis
set_expected = set(expected_dates)
set_observed = set(all_observed_dates)

missing_dates = sorted(list(set_expected - set_observed))
unexpected_dates = sorted(list(set_observed - set_expected))

print(f"\nMissing sessions count: {len(missing_dates)}")
print(f"Unexpected sessions count: {len(unexpected_dates)}")
print(f"Missing sessions list:\n{missing_dates}")
if unexpected_dates:
    print(f"Unexpected sessions list:\n{unexpected_dates}")

# 4. Yearly breakdown
yearly_stats = {}
for yr in range(2010, 2022):
    yr_str = str(yr)
    exp_yr = [d for d in expected_dates if d.startswith(yr_str)]
    obs_yr = [d for d in all_observed_dates if d.startswith(yr_str)]
    miss_yr = [d for d in missing_dates if d.startswith(yr_str)]
    unexp_yr = [d for d in unexpected_dates if d.startswith(yr_str)]
    
    missing_rate_pct = (len(miss_yr) / len(exp_yr)) * 100.0 if exp_yr else 0.0
    
    yearly_stats[yr_str] = {
        "expected_sessions": len(exp_yr),
        "observed_sessions": len(obs_yr),
        "missing_sessions": len(miss_yr),
        "unexpected_sessions": len(unexp_yr),
        "missing_rate_pct": missing_rate_pct,
        "missing_dates": miss_yr
    }

total_missing_rate = (len(missing_dates) / len(expected_dates)) * 100.0
print(f"\nOverall 2010-2021 Missing Rate: {len(missing_dates)} / {len(expected_dates)} = {total_missing_rate:.3f}% (Protocol threshold: <= 1.0%)")

print("\n--- Yearly Summary ---")
for yr_str, st in sorted(yearly_stats.items()):
    print(f"{yr_str}: Expected={st['expected_sessions']}, Observed={st['observed_sessions']}, Missing={st['missing_sessions']} ({st['missing_rate_pct']:.2f}%), Unexpected={st['unexpected_sessions']}")
    if st['missing_dates']:
        print(f"   Missing dates in {yr_str}: {st['missing_dates']}")

# 5. Timestamp analysis across vintages
readtimes_summary = {}
for qd, ts_set in observed_readtimes_by_date.items():
    yr = qd[:4]
    if yr not in readtimes_summary:
        readtimes_summary[yr] = {"distinct_timestamps": set(), "early_closes": []}
    for ts in ts_set:
        readtimes_summary[yr]["distinct_timestamps"].add(ts)
        # Check early closes (e.g. 13:00)
        if "13:00" in ts or "13:15" in ts:
            readtimes_summary[yr]["early_closes"].append((qd, ts))

print("\n--- Timestamp Analysis Across Vintages ---")
for yr in sorted(readtimes_summary):
    times = sorted(readtimes_summary[yr]["distinct_timestamps"])
    # Just show time components
    time_suffixes = sorted(set([t.split()[-1] if ' ' in t else t for t in times]))
    early_closes = readtimes_summary[yr]["early_closes"]
    print(f"Year {yr}: Time components={time_suffixes}, Total early close days={len(early_closes)}")
    if early_closes:
        print(f"   Sample early closes: {early_closes[:3]}")

# 6. Save audit results to output
os.makedirs("output/stage6_audit", exist_ok=True)
audit_export = {
    "audit_period": "2010-2021 (12 Calendar Years)",
    "denominator_definition": "Official active exchange trading days from S&P 500 cash index (^GSPC) accounting for federal holidays and unscheduled closures (Sandy 2012, Bush funeral 2018)",
    "total_expected_sessions": len(expected_dates),
    "total_observed_sessions": len(all_observed_dates),
    "total_missing_sessions": len(missing_dates),
    "total_unexpected_sessions": len(unexpected_dates),
    "overall_missing_rate_pct": total_missing_rate,
    "passes_1pct_threshold": total_missing_rate <= 1.0,
    "missing_dates": missing_dates,
    "yearly_statistics": yearly_stats,
    "readtimes_summary": {
        yr: {
            "distinct_time_suffixes": sorted(list(set([t.split()[-1] if ' ' in t else t for t in readtimes_summary[yr]["distinct_timestamps"]]))),
            "early_closes_count": len(readtimes_summary[yr]["early_closes"]),
            "early_closes": readtimes_summary[yr]["early_closes"]
        } for yr in readtimes_summary
    }
}

with open("output/stage6_audit/session_continuity_2010_2021.json", "w") as f:
    json.dump(audit_export, f, indent=2)

print("\nSaved full audit to output/stage6_audit/session_continuity_2010_2021.json")
