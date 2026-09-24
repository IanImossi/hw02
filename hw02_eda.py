"""
===============================================================================
Script:       hw02_eda.py
Purpose:      Exploratory data analysis (EDA) and validation profile for HW2
Dataset:      fact_transactions.csv - Wildcat Capital client transactions,
              Jan 2020 - Dec 2024 (expected 298,772 rows x 9 columns)
Author:       Ian
Generated:    2026-09-23 (with Claude Cowork)
Course:       MIS3060 Business Intelligence with AI - HW2

Run from the HW2 folder:
    python hw02_eda.py

Outputs:
    hw02/charts/hist_amount.png
    hw02/charts/box_amount_by_type.png
    hw02/charts/scatter_shares_amount.png
    hw02/hw02_profile.txt
===============================================================================
"""

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")  # save charts to files without needing a display window
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------------------------------------------------------
# Paths (resolved relative to this script, so it works from any working dir)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "raw" / "fact_transactions.csv"
ALT_DATA_PATH = BASE_DIR / "02_Data" / "Raw" / "fact_transactions.csv"
OUT_DIR = BASE_DIR / "hw02"
CHART_DIR = OUT_DIR / "charts"
PROFILE_PATH = OUT_DIR / "hw02_profile.txt"

EXPECTED_SHAPE = (298772, 9)

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

# Everything reported is collected here and also written to hw02_profile.txt
report_lines = []


def report(text=""):
    """Print a line and keep it for the plain-text profile."""
    print(text)
    report_lines.append(str(text))


def section(number, title):
    report("")
    report("=" * 78)
    report(f"{number}. {title}")
    report("=" * 78)


# -----------------------------------------------------------------------------
# 1. Load data
# -----------------------------------------------------------------------------
if DATA_PATH.exists():
    csv_path = DATA_PATH
elif ALT_DATA_PATH.exists():
    csv_path = ALT_DATA_PATH
    print(f"NOTE: {DATA_PATH} not found - using {ALT_DATA_PATH}")
else:
    sys.exit(f"ERROR: could not find fact_transactions.csv at {DATA_PATH}")

# Keep txn_date as a plain object (string) column, matching the benchmark.
# (pandas 3 would otherwise load text as the newer "str" dtype.)
df = pd.read_csv(csv_path, dtype={"txn_date": object})
df["txn_date"] = df["txn_date"].astype(object)

report("HW2 EDA PROFILE - fact_transactions.csv")
report(f"Source file: {csv_path.relative_to(BASE_DIR)}")

# -----------------------------------------------------------------------------
# 2. Shape, column names and data types
# -----------------------------------------------------------------------------
section(2, "SHAPE, COLUMNS AND DATA TYPES")
report(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
if df.shape != EXPECTED_SHAPE:
    report(f"WARNING: shape {df.shape} does not match expected {EXPECTED_SHAPE}!")
else:
    report(f"Shape check: OK (matches expected {EXPECTED_SHAPE})")
report("")
report(df.dtypes.rename("dtype").to_frame().to_string())

# -----------------------------------------------------------------------------
# 3. Missing values per column
# -----------------------------------------------------------------------------
section(3, "MISSING VALUES PER COLUMN")
missing = pd.DataFrame({
    "missing": df.isna().sum(),
    "pct_missing": (df.isna().mean() * 100).round(2),
})
report(missing.to_string())

# -----------------------------------------------------------------------------
# 4. Summary statistics for numeric columns
# -----------------------------------------------------------------------------
section(4, "SUMMARY STATISTICS (NUMERIC COLUMNS)")
stats = df.describe().T.rename(columns={"50%": "median", "25%": "25th pct",
                                        "75%": "75th pct"})
report(stats.to_string())

# -----------------------------------------------------------------------------
# 5. txn_type value counts and percents
# -----------------------------------------------------------------------------
section(5, "TXN_TYPE VALUE COUNTS (MOST TO LEAST FREQUENT)")
type_counts = pd.DataFrame({
    "count": df["txn_type"].value_counts(),
    "percent": (df["txn_type"].value_counts(normalize=True) * 100).round(2),
})
report(type_counts.to_string())
unique_types = sorted(df["txn_type"].dropna().unique())
report("")
report(f"Unique txn_type values: {len(unique_types)}")
for t in unique_types:
    report(f"  - {t}")

# -----------------------------------------------------------------------------
# 6. Unique clients, advisors, securities
# -----------------------------------------------------------------------------
section(6, "UNIQUE ENTITIES")
report(f"Unique clients:    {df['client_id'].nunique():,}")
report(f"Unique advisors:   {df['advisor_id'].nunique():,}")
report(f"Unique securities: {df['security_id'].nunique():,} (excludes nulls)")
report(f"Unique txn_types: {df['txn_type'].nunique():,} "
       f"({', '.join(sorted(df['txn_type'].dropna().unique()))})")

# -----------------------------------------------------------------------------
# 7. Date range (txn_date is stored as text; parse a copy for min/max)
# -----------------------------------------------------------------------------
section(7, "TRANSACTION DATE RANGE")
txn_dates = pd.to_datetime(df["txn_date"], errors="coerce")
report(f"txn_date stored as: {df['txn_date'].dtype}")
report(f"Earliest txn_date:  {txn_dates.min().date()}")
report(f"Latest txn_date:    {txn_dates.max().date()}")
bad_dates = txn_dates.isna().sum() - df["txn_date"].isna().sum()
report(f"Unparseable dates:  {bad_dates}")

# -----------------------------------------------------------------------------
# 8. Duplicate txn_id check
# -----------------------------------------------------------------------------
section(8, "DUPLICATE CHECK")
dupe_count = df["txn_id"].duplicated().sum()
report(f"Duplicate txn_id values: {dupe_count:,}")

# -----------------------------------------------------------------------------
# 9. amount: mean, median, skewness
# -----------------------------------------------------------------------------
section(9, "AMOUNT DISTRIBUTION")
amt_mean = df["amount"].mean()
amt_median = df["amount"].median()
amt_skew = df["amount"].skew()
shape_label = ("right-skewed" if amt_skew > 0.5
               else "left-skewed" if amt_skew < -0.5 else "roughly symmetric")
report(f"Mean amount:     ${amt_mean:,.2f}")
report(f"Median amount:   ${amt_median:,.2f}")
report(f"Skewness:        {amt_skew:.2f} ({shape_label})")

# -----------------------------------------------------------------------------
# 10. Group by txn_type
# -----------------------------------------------------------------------------
section(10, "AMOUNT BY TXN_TYPE (SORTED BY MEAN DESC)")
by_type = (df.groupby("txn_type")["amount"]
             .agg(count="count", mean_amount="mean", median_amount="median")
             .round(2)
             .sort_values("mean_amount", ascending=False))
report(by_type.to_string())

# -----------------------------------------------------------------------------
# 11. Correlation matrix: shares, price, amount
# -----------------------------------------------------------------------------
section(11, "CORRELATION MATRIX (shares, price, amount)")
corr_cols = ["shares", "price", "amount"]
corr = df[corr_cols].corr().round(2)
report(corr.to_string())

pairs = []
for i, a in enumerate(corr_cols):
    for b in corr_cols[i + 1:]:
        pairs.append((a, b, corr.loc[a, b]))
pairs.sort(key=lambda p: abs(p[2]), reverse=True)
report("")
report("Three strongest correlations (by absolute value, self-pairs excluded):")
for rank, (a, b, r) in enumerate(pairs[:3], start=1):
    report(f"  {rank}. {a} - {b}: {r:.2f}")

# -----------------------------------------------------------------------------
# 12. Negative shares by txn_type
# -----------------------------------------------------------------------------
section(12, "SHARES BY TXN_TYPE (MIN, MAX, NEGATIVE COUNT)")
shares_by_type = df.groupby("txn_type")["shares"].agg(
    min_shares="min",
    max_shares="max",
    negative_count=lambda s: int((s < 0).sum()),
)
report(shares_by_type.to_string())
report(f"Total negative shares rows: {int((df['shares'] < 0).sum()):,}")

# -----------------------------------------------------------------------------
# 13. Charts
# -----------------------------------------------------------------------------
section(13, "CHARTS SAVED")
CHART_DIR.mkdir(parents=True, exist_ok=True)

# 13a. Histogram of amount with mean and median lines
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df["amount"], bins=60, color="#4C72B0", edgecolor="white")
ax.axvline(amt_mean, color="#C44E52", linestyle="--", linewidth=2,
           label=f"Mean = ${amt_mean:,.2f}")
ax.axvline(amt_median, color="#2CA02C", linestyle="-", linewidth=2,
           label=f"Median = ${amt_median:,.2f}")
ax.set_title("Distribution of Transaction Amount")
ax.set_xlabel("Amount ($)")
ax.set_ylabel("Number of transactions")
ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
ax.legend()
fig.tight_layout()
hist_path = CHART_DIR / "hist_amount.png"
fig.savefig(hist_path, dpi=150)
plt.close(fig)
report(f"Saved: {hist_path.relative_to(BASE_DIR)}")

# 13b. Horizontal box plot of amount by txn_type (ordered by mean, as in item 10)
type_order = list(by_type.index)
fig, ax = plt.subplots(figsize=(10, 6))
ax.boxplot([df.loc[df["txn_type"] == t, "amount"] for t in type_order],
           vert=False, patch_artist=True,
           boxprops=dict(facecolor="#DCE6F2"),
           medianprops=dict(color="#C44E52", linewidth=2),
           flierprops=dict(marker=".", markersize=2, alpha=0.3))
ax.set_yticks(range(1, len(type_order) + 1), type_order)
ax.set_title("Transaction Amount by Transaction Type")
ax.set_xlabel("Amount ($)")
ax.set_ylabel("Transaction type")
ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
fig.tight_layout()
box_path = CHART_DIR / "box_amount_by_type.png"
fig.savefig(box_path, dpi=150)
plt.close(fig)
report(f"Saved: {box_path.relative_to(BASE_DIR)}")

# 13c. Scatter of shares vs amount colored by txn_type
# (only rows that have a shares value can be plotted)
scatter_df = df.dropna(subset=["shares", "amount"])
fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.get_cmap("tab10")
for i, t in enumerate(sorted(scatter_df["txn_type"].unique())):
    sub = scatter_df[scatter_df["txn_type"] == t]
    ax.scatter(sub["shares"], sub["amount"], s=4, alpha=0.3,
               color=colors(i), label=f"{t} (n={len(sub):,})")
ax.set_title("Shares vs. Amount by Transaction Type")
ax.set_xlabel("Shares")
ax.set_ylabel("Amount ($)")
ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
ax.legend(markerscale=4, title="txn_type")
fig.tight_layout()
scatter_path = CHART_DIR / "scatter_shares_amount.png"
fig.savefig(scatter_path, dpi=150)
plt.close(fig)
report(f"Saved: {scatter_path.relative_to(BASE_DIR)}")
report(f"Rows plotted in scatter: {len(scatter_df):,} "
       f"({len(df) - len(scatter_df):,} rows have no shares value)")

# -----------------------------------------------------------------------------
# Save the plain-text profile (items 2-13)
# -----------------------------------------------------------------------------
OUT_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
print(f"\nProfile saved: {PROFILE_PATH.relative_to(BASE_DIR)}")
