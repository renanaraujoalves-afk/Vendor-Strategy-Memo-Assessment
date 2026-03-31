"""
Step 4: Audit sample for human review.

Selects:
  • Top 5% by spend      (~19 vendors) — highest financial risk if wrong
  • Random 5% sample     (~19 vendors) — statistical coverage
  (deduped, so total ≤ ~38 vendors)

Prints the audit table to the terminal for the user to review interactively,
then writes the audit sample and user feedback to:
  outputs/validation_recommendations.md
"""

import csv
import random
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
INPUT_CSV = ROOT / "outputs" / "vendors_final.csv"
VALIDATION_MD = ROOT / "outputs" / "validation_recommendations.md"

TOP_PCT = 0.05
RANDOM_PCT = 0.05

# ---------------------------------------------------------------------------

def parse_cost(raw: str) -> float:
    cleaned = raw.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def load_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): v.strip() for k, v in row.items()})
    return rows


def fmt_row(row: dict, idx: int) -> str:
    cost = parse_cost(row.get("Last 12 months Cost (USD)", "$0"))
    return (
        f"  [{idx:>2}] {row['Vendor Name']:<40} "
        f"${cost:>12,.0f}  "
        f"{row.get('Department', ''):<25} "
        f"{row.get('Suggestions (Consolidate / Terminate / Optimize costs)', ''):<12} "
        f"{row.get('Recommendation Rationale', '')}"
    )


def main():
    print("=== Step 4: Audit Sample for Human Review ===\n")

    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found. Run step3_recommend.py first.")
        sys.exit(1)

    rows = load_csv(INPUT_CSV)
    n = len(rows)
    top_n = max(1, int(n * TOP_PCT))
    rand_n = max(1, int(n * RANDOM_PCT))

    print(f"Total vendors: {n}")
    print(f"Top {TOP_PCT*100:.0f}% by spend -> {top_n} vendors")
    print(f"Random {RANDOM_PCT*100:.0f}% sample -> {rand_n} vendors")

    # Sort by spend for top selection
    sorted_rows = sorted(rows, key=lambda r: parse_cost(r.get("Last 12 months Cost (USD)", "$0")), reverse=True)

    top_sample = sorted_rows[:top_n]
    top_names = {r["Vendor Name"] for r in top_sample}

    # Random from the rest (avoid duplicating top sample)
    remaining = [r for r in rows if r["Vendor Name"] not in top_names]
    rand_sample = random.sample(remaining, min(rand_n, len(remaining)))

    # Combine and sort by spend for display
    audit_rows = sorted(top_sample + rand_sample,
                        key=lambda r: parse_cost(r.get("Last 12 months Cost (USD)", "$0")),
                        reverse=True)

    print(f"\nTotal audit sample: {len(audit_rows)} vendors\n")

    # ---------------------------------------------------------------------------
    # Display audit table
    # ---------------------------------------------------------------------------
    header = (
        f"  {'#':>4}  {'Vendor Name':<40} {'Spend (USD)':>12}  "
        f"{'Department':<25} {'Recommendation':<12} Rationale"
    )
    sep = "-" * len(header)

    print(sep)
    print("  TOP 5% BY SPEND")
    print(sep)
    print(header)
    print(sep)
    for i, row in enumerate(top_sample):
        print(fmt_row(row, i + 1))

    print()
    print(sep)
    print("  RANDOM 5% SAMPLE")
    print(sep)
    print(header)
    print(sep)
    rand_sorted = sorted(rand_sample, key=lambda r: parse_cost(r.get("Last 12 months Cost (USD)", "$0")), reverse=True)
    for i, row in enumerate(rand_sorted):
        print(fmt_row(row, i + 1))
    print(sep)

    # ---------------------------------------------------------------------------
    # Interactive feedback
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("AUDIT INSTRUCTIONS")
    print("=" * 70)
    print("Review the vendors above. For each issue you spot, enter a correction")
    print("in the format:  <Vendor Name> | <correct recommendation> | <note>")
    print("Type 'done' when finished, or press Enter to skip.\n")

    feedback_lines = []
    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break
        if line.lower() in ("done", "exit", "quit", ""):
            break
        feedback_lines.append(line)

    # ---------------------------------------------------------------------------
    # Write Markdown validation report
    # ---------------------------------------------------------------------------
    total_spend = sum(parse_cost(r.get("Last 12 months Cost (USD)", "$0")) for r in rows)
    top_spend = sum(parse_cost(r.get("Last 12 months Cost (USD)", "$0")) for r in top_sample)

    rec_col = "Suggestions (Consolidate / Terminate / Optimize costs)"
    rec_counts: dict[str, int] = {}
    rec_spend: dict[str, float] = {}
    for row in rows:
        rec = row.get(rec_col, "Unknown")
        cost = parse_cost(row.get("Last 12 months Cost (USD)", "$0"))
        rec_counts[rec] = rec_counts.get(rec, 0) + 1
        rec_spend[rec] = rec_spend.get(rec, 0.0) + cost

    md = [
        "# Validation Report — Strategic Recommendations",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Source:** `vendors_final.csv` ({n} vendors, total spend: ${total_spend:,.0f})  ",
        "",
        "---",
        "",
        "## 1. Recommendation Summary",
        "",
        "| Recommendation | Vendor Count | Total Spend | % of Spend |",
        "|---------------|-------------|-------------|------------|",
    ]
    for rec in ["Optimize", "Consolidate", "Terminate"]:
        cnt = rec_counts.get(rec, 0)
        sp = rec_spend.get(rec, 0.0)
        pct = sp / total_spend * 100 if total_spend else 0
        md.append(f"| {rec} | {cnt} | ${sp:,.0f} | {pct:.1f}% |")
    md += [
        f"| **Total** | **{n}** | **${total_spend:,.0f}** | **100%** |",
        "",
        "---",
        "",
        "## 2. Audit Sample — Top 5% by Spend",
        f"({top_n} vendors, representing ${top_spend:,.0f} / {top_spend/total_spend*100:.1f}% of total spend)",
        "",
        "| Vendor | Spend | Department | Recommendation | Rationale |",
        "|--------|-------|-----------|---------------|-----------|",
    ]
    for row in top_sample:
        cost = parse_cost(row.get("Last 12 months Cost (USD)", "$0"))
        md.append(
            f"| {row['Vendor Name']} | ${cost:,.0f} | "
            f"{row.get('Department', '')} | "
            f"{row.get(rec_col, '')} | "
            f"{row.get('Recommendation Rationale', '')} |"
        )

    md += [
        "",
        "---",
        "",
        "## 3. Audit Sample — Random 5%",
        f"({rand_n} vendors randomly selected from remaining {n - top_n})",
        "",
        "| Vendor | Spend | Department | Recommendation | Rationale |",
        "|--------|-------|-----------|---------------|-----------|",
    ]
    for row in rand_sorted:
        cost = parse_cost(row.get("Last 12 months Cost (USD)", "$0"))
        md.append(
            f"| {row['Vendor Name']} | ${cost:,.0f} | "
            f"{row.get('Department', '')} | "
            f"{row.get(rec_col, '')} | "
            f"{row.get('Recommendation Rationale', '')} |"
        )

    md += [
        "",
        "---",
        "",
        "## 4. Human Auditor Feedback",
        "",
    ]

    if feedback_lines:
        md += [
            "The following corrections were noted during the audit review:",
            "",
            "| Vendor | Corrected Recommendation | Note |",
            "|--------|--------------------------|------|",
        ]
        for line in feedback_lines:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                md.append(f"| {parts[0]} | {parts[1]} | {parts[2]} |")
            else:
                md.append(f"| {line} | | |")
        md.append("")
        md.append(f"**{len(feedback_lines)} correction(s) noted.** Apply these to `vendors_final.csv` manually if needed.")
    else:
        md.append("No corrections noted by the auditor. Recommendations accepted as-is.")

    md += [
        "",
        "---",
        "",
        "## 5. Audit Methodology",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Total vendors audited | {len(audit_rows)} of {n} ({len(audit_rows)/n*100:.1f}%) |",
        f"| Top spend selection | Top {TOP_PCT*100:.0f}% by 12-month spend ({top_n} vendors) |",
        f"| Random selection | {RANDOM_PCT*100:.0f}% random sample from remaining vendors ({rand_n} vendors) |",
        "| Auditor | Human (VP of Operations) |",
        f"| Review date | {datetime.now().strftime('%Y-%m-%d')} |",
        "",
        "_Generated by `scripts/step4_audit.py`_",
    ]

    VALIDATION_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"\nValidation report saved -> {VALIDATION_MD}")

    if feedback_lines:
        print(f"\n{len(feedback_lines)} correction(s) logged. Review {VALIDATION_MD.name} for details.")
    else:
        print("\nNo corrections noted. All sampled recommendations accepted.")

    print("\n[OK] Step 4 complete. Part 1 analysis is done!")
    print("  Next: run /step2-opportunities for Part 2.")


if __name__ == "__main__":
    main()
