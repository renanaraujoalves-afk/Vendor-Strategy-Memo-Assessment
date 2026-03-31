"""
Step 1: Categorize vendors — assign Department and 1-line Description.

Calls Claude API in batches of 60 vendors.
Outputs:
  outputs/vendors_categorized.csv   — full dataset with filled Department & Description
  outputs/pivot_summary.csv         — spend pivot by Department
  outputs/pivot_summary.txt         — human-readable pivot table
"""

import csv
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
INPUT_CSV = ROOT / "inputs" / "Vendor Analysis Assessment.csv"
OUTPUT_CSV = ROOT / "outputs" / "vendors_categorized.csv"
PIVOT_CSV = ROOT / "outputs" / "pivot_summary.csv"
PIVOT_TXT = ROOT / "outputs" / "pivot_summary.txt"

VALID_DEPARTMENTS = [
    "Engineering", "Facilities", "G&A", "Legal", "M&A",
    "Marketing", "SaaS", "Product", "Professional Services",
    "Sales", "Support", "Finance",
]

BATCH_SIZE = 60

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_cost(raw: str) -> float:
    """Convert '$1,234,567' → 1234567.0"""
    cleaned = raw.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def build_prompt(batch: list[dict]) -> str:
    dept_list = ", ".join(VALID_DEPARTMENTS)
    lines = "\n".join(
        f'{i+1}. "{r["vendor"]}" | ${r["cost_float"]:,.0f}/yr'
        for i, r in enumerate(batch)
    )
    return f"""You are a VP of Operations classifying vendors for a recently acquired ~$1B SaaS/tech company.

VALID DEPARTMENTS (use exactly one per vendor):
{dept_list}

For each vendor below, return ONLY a valid JSON array — no markdown fences, no commentary.
Each element must have exactly these keys:
  "vendor"      : exact vendor name as given
  "department"  : one department from the list above
  "description" : ONE concise sentence (≤ 120 chars) describing what the vendor does.
                  Be specific: name the product category and service location, not just "provides business services".
                  Good example: "European Cloud telephony platform for customer support call routing"
                  Bad example: "Business services provider"

VENDORS:
{lines}

Return JSON array only."""


def call_claude(client: anthropic.Anthropic, prompt: str, attempt: int = 1) -> list[dict]:
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
            raw = raw.rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        if attempt < 3:
            print(f"    Retrying (attempt {attempt+1}) — {e}")
            time.sleep(2)
            return call_claude(client, prompt, attempt + 1)
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Step 1: Categorize Vendors ===\n")

    client = anthropic.Anthropic()

    # Read input
    rows = []
    with open(INPUT_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            rows.append({
                "vendor": cleaned.get("Vendor Name", ""),
                "cost_raw": cleaned.get("Last 12 months Cost (USD)", "$0"),
                "cost_float": parse_cost(cleaned.get("Last 12 months Cost (USD)", "$0")),
                "department": cleaned.get("Department", ""),
                "description": cleaned.get("1-line Description on what the Vendor does", ""),
                "suggestion": cleaned.get("Suggestions (Consolidate / Terminate / Optimize costs)", ""),
            })

    print(f"Loaded {len(rows)} vendors from input CSV.")

    # Only categorize rows missing Department or Description
    to_classify = [r for r in rows if not r["department"] or not r["description"]]
    already_done = len(rows) - len(to_classify)
    if already_done:
        print(f"  {already_done} vendors already have data — skipping.")
    print(f"  {len(to_classify)} vendors to classify via Claude.\n")

    # Build lookup for results
    results: dict[str, dict] = {}

    batches = [to_classify[i:i+BATCH_SIZE] for i in range(0, len(to_classify), BATCH_SIZE)]
    for idx, batch in enumerate(batches):
        print(f"  Batch {idx+1}/{len(batches)} ({len(batch)} vendors)…", end=" ", flush=True)
        prompt = build_prompt(batch)
        classified = call_claude(client, prompt)
        # Index by vendor name (case-insensitive fallback)
        for item in classified:
            results[item["vendor"].strip()] = item
        print("done.")
        if idx < len(batches) - 1:
            time.sleep(0.5)

    # Merge back into rows
    unmatched = 0
    for row in rows:
        if row["vendor"] in results:
            r = results[row["vendor"]]
            row["department"] = r.get("department", row["department"]).strip()
            row["description"] = r.get("description", row["description"]).strip()
        elif not row["department"] or not row["description"]:
            unmatched += 1

    if unmatched:
        print(f"\n  Warning: {unmatched} vendors could not be matched from API response.")

    # Write output CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "Vendor Name", "Department", "Last 12 months Cost (USD)",
        "1-line Description on what the Vendor does",
        "Suggestions (Consolidate / Terminate / Optimize costs)",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "Vendor Name": row["vendor"],
                "Department": row["department"],
                "Last 12 months Cost (USD)": row["cost_raw"],
                "1-line Description on what the Vendor does": row["description"],
                "Suggestions (Consolidate / Terminate / Optimize costs)": row["suggestion"],
            })

    print(f"\nCategorized CSV saved -> {OUTPUT_CSV}")

    # ------------------------------------------------------------------
    # Pivot table: spend by Department
    # ------------------------------------------------------------------
    dept_spend: dict[str, float] = {}
    dept_count: dict[str, int] = {}
    total_spend = 0.0

    for row in rows:
        dept = row["department"] or "UNCLASSIFIED"
        spend = row["cost_float"]
        dept_spend[dept] = dept_spend.get(dept, 0.0) + spend
        dept_count[dept] = dept_count.get(dept, 0) + 1
        total_spend += spend

    sorted_depts = sorted(dept_spend.items(), key=lambda x: x[1], reverse=True)

    # CSV pivot
    with open(PIVOT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Department", "Vendor Count", "Total Spend (USD)", "% of Total"])
        for dept, spend in sorted_depts:
            pct = (spend / total_spend * 100) if total_spend else 0
            writer.writerow([dept, dept_count[dept], f"${spend:,.0f}", f"{pct:.1f}%"])
        writer.writerow(["TOTAL", len(rows), f"${total_spend:,.0f}", "100.0%"])

    # Text pivot
    col_w = [28, 14, 22, 10]
    header = f"{'Department':<{col_w[0]}} {'Vendors':>{col_w[1]}} {'Total Spend (USD)':>{col_w[2]}} {'% Total':>{col_w[3]}}"
    sep = "-" * sum(col_w + [3 * 1])

    lines_txt = [
        "VENDOR SPEND BY DEPARTMENT",
        f"(Total vendors: {len(rows)}, Total spend: ${total_spend:,.0f})",
        "",
        header,
        sep,
    ]
    for dept, spend in sorted_depts:
        pct = (spend / total_spend * 100) if total_spend else 0
        lines_txt.append(
            f"{dept:<{col_w[0]}} {dept_count[dept]:>{col_w[1]}} "
            f"{'$'+f'{spend:,.0f}':>{col_w[2]}} {pct:>{col_w[3]-1}.1f}%"
        )
    lines_txt += [sep, f"{'TOTAL':<{col_w[0]}} {len(rows):>{col_w[1]}} {'$'+f'{total_spend:,.0f}':>{col_w[2]}} {'100.0':>{col_w[3]-1}}%"]

    pivot_text = "\n".join(lines_txt)
    PIVOT_TXT.write_text(pivot_text, encoding="utf-8")

    print(f"Pivot summary saved -> {PIVOT_CSV}")
    print(f"Pivot text saved   -> {PIVOT_TXT}\n")
    print(pivot_text)
    print("\nStep 1 complete. Run step2_validate.py next.")


if __name__ == "__main__":
    main()
