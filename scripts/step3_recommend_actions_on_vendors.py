"""
Step 3: Assign strategic recommendations (Terminate / Consolidate / Optimize).

Uses Claude API in batches, applying explicit guidelines and assumptions.
Adds a "Recommendation" column and a "Recommendation Rationale" column.

Input:  outputs/vendors_categorized.csv
Output: outputs/vendors_final.csv
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
ROOT = Path(__file__).parent.parent
INPUT_CSV = ROOT / "outputs" / "vendors_categorized.csv"
OUTPUT_CSV = ROOT / "outputs" / "vendors_final.csv"

BATCH_SIZE = 50

GUIDELINES = """
RECOMMENDATION GUIDELINES
==========================

You are acting as VP of Operations for a recently acquired ~$1B ARR SaaS/tech company.
Assign ONE of: Terminate, Consolidate, Optimize.

--- TERMINATE ---
Use when the vendor:
  • Spends < $5,000/year with no clear strategic value
  • Is redundant — a higher-priority vendor in the same department already covers the function
  • Is a one-time or legacy engagement with no ongoing value
  • Provides a service the company can handle internally at negligible cost
  • Is clearly a duplicate tool (e.g., third survey tool when two already exist)

--- CONSOLIDATE ---
Use when:
  • Two or more vendors serve the same core function within the same department
    (e.g., multiple cloud storage providers, multiple travel management platforms,
     multiple video-conferencing tools, multiple CRM or ERP systems)
  • Consolidation would reduce vendor count without losing capability
  • The vendor is the SMALLER of the overlapping vendors (flag both, but prioritize the smaller one for elimination)

--- OPTIMIZE ---
Use when:
  • The vendor is strategically necessary (critical infrastructure, compliance, key SaaS platform)
  • There is a cost reduction opportunity: renegotiate contract, reduce seat count, move to lower tier,
    implement usage caps, or explore competitive bids
  • The vendor is the dominant player in a consolidated pair (keep, but optimize spend)
  • Spend is high relative to typical market pricing (>$50K/year for niche tools suggests over-contracting)
  • The vendor provides a unique service with no clear substitute

ASSUMPTIONS
===========
1. Company has ~$1B revenue; individual vendors under $5K/year have low leverage — default Terminate unless strategic.
2. Facilities vendors (office leases, co-working spaces) -> Optimize if active, Terminate if redundant locations.
3. Insurance, compliance, legal, audit vendors -> Optimize by default (rarely terminable).
4. SaaS tools with overlapping scope (e.g., multiple BI tools, multiple project management tools) -> Consolidate.
5. Engineering infrastructure (cloud providers, CDN, monitoring) -> Optimize (rarely terminate core infra).
6. Marketing agencies and consultants -> Optimize or Terminate based on spend and strategic fit.
7. Professional Services (one-time engagements) -> Terminate if project is complete; Optimize if ongoing.
8. When in doubt (unclear purpose, ambiguous name), assign Optimize with a rationale noting the uncertainty.
"""


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


def build_prompt(batch: list[dict]) -> str:
    lines = []
    for i, r in enumerate(batch):
        cost = parse_cost(r.get("Last 12 months Cost (USD)", "$0"))
        lines.append(
            f'{i+1}. "{r["Vendor Name"]}" | Dept: {r["Department"]} | Spend: ${cost:,.0f}/yr\n'
            f'   Description: {r.get("1-line Description on what the Vendor does", "")}'
        )
    vendor_block = "\n".join(lines)

    return f"""{GUIDELINES}

VENDORS TO CLASSIFY:
{vendor_block}

Return ONLY a valid JSON array — no markdown, no commentary.
Each element must have exactly these keys:
  "vendor"         : exact vendor name as given
  "recommendation" : "Terminate" | "Consolidate" | "Optimize"
  "rationale"      : one concise sentence (≤ 120 chars) explaining the recommendation

JSON array only:"""


def call_claude(client: anthropic.Anthropic, prompt: str, attempt: int = 1) -> list[dict]:
    try:
        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
            raw = raw.rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except Exception as e:
        if attempt < 3:
            print(f"    Retrying (attempt {attempt+1}) — {e}")
            time.sleep(2)
            return call_claude(client, prompt, attempt + 1)
        raise


def main():
    print("=== Step 3: Strategic Recommendations ===\n")

    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found. Run step1_categorize.py first.")
        sys.exit(1)

    client = anthropic.Anthropic()
    rows = load_csv(INPUT_CSV)
    print(f"Loaded {len(rows)} vendors.")

    # Only process rows missing a recommendation
    to_process = [r for r in rows if not r.get("Suggestions (Consolidate / Terminate / Optimize costs)")]
    already_done = len(rows) - len(to_process)
    if already_done:
        print(f"  {already_done} vendors already have recommendations — skipping.")
    print(f"  {len(to_process)} vendors to classify.\n")

    results: dict[str, dict] = {}

    batches = [to_process[i:i+BATCH_SIZE] for i in range(0, len(to_process), BATCH_SIZE)]
    for idx, batch in enumerate(batches):
        print(f"  Batch {idx+1}/{len(batches)} ({len(batch)} vendors)…", end=" ", flush=True)
        prompt = build_prompt(batch)
        classified = call_claude(client, prompt)
        for item in classified:
            results[item["vendor"].strip()] = item
        print("done.")
        if idx < len(batches) - 1:
            time.sleep(0.5)

    # Merge results
    unmatched = 0
    for row in rows:
        if row["Vendor Name"] in results:
            r = results[row["Vendor Name"]]
            row["Suggestions (Consolidate / Terminate / Optimize costs)"] = r.get("recommendation", "")
            row["Recommendation Rationale"] = r.get("rationale", "")
        elif not row.get("Suggestions (Consolidate / Terminate / Optimize costs)"):
            unmatched += 1

    if unmatched:
        print(f"  Warning: {unmatched} vendors not matched from API response.")

    # Summary stats
    rec_counts: dict[str, int] = {}
    for row in rows:
        rec = row.get("Suggestions (Consolidate / Terminate / Optimize costs)", "Unknown")
        rec_counts[rec] = rec_counts.get(rec, 0) + 1

    print("\nRecommendation breakdown:")
    for rec, count in sorted(rec_counts.items()):
        pct = count / len(rows) * 100
        print(f"  {rec}: {count} ({pct:.1f}%)")

    # Write output CSV
    fieldnames = [
        "Vendor Name", "Department", "Last 12 months Cost (USD)",
        "1-line Description on what the Vendor does",
        "Suggestions (Consolidate / Terminate / Optimize costs)",
        "Recommendation Rationale",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nFinal vendor CSV saved -> {OUTPUT_CSV}")
    print("\n[OK] Step 3 complete. Run step4_audit.py next.")


if __name__ == "__main__":
    main()
