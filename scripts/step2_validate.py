"""
Step 2: Validate categorization output.

Structural checks (Python):
  [OK] Row count matches source CSV
  [OK] All departments are from the valid list
  [OK] No blank Department or Description
  [OK] Description length: 10–180 characters
  [OK] No obviously generic descriptions

Claude quality check:
  - Samples up to 40 descriptions (evenly spread across departments)
  - Asks Claude to rate each for specificity and flag weak ones

Output:
  outputs/validation_categorization.md
"""

import csv
import json
import os
import random
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic

# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
SOURCE_CSV = ROOT / "inputs" / "Vendor Analysis Assessment.csv"
CATEGORIZED_CSV = ROOT / "outputs" / "vendors_categorized.csv"
VALIDATION_MD = ROOT / "outputs" / "validation_categorization.md"

VALID_DEPARTMENTS = {
    "Engineering", "Facilities", "G&A", "Legal", "M&A",
    "Marketing", "SaaS", "Product", "Professional Services",
    "Sales", "Support", "Finance",
}

GENERIC_PHRASES = [
    "business services", "service provider", "provides services",
    "technology company", "software company", "consulting firm",
    "vendor", "supplier", "solutions provider", "it services",
]

SAMPLE_SIZE = 40  # descriptions sent to Claude for quality review


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


def is_generic(desc: str) -> bool:
    d = desc.lower()
    return any(phrase in d for phrase in GENERIC_PHRASES)


# ---------------------------------------------------------------------------
def structural_checks(source_rows, cat_rows) -> list[dict]:
    """Returns list of issue dicts: {check, status, detail}"""
    issues = []

    # 1. Row count
    if len(source_rows) == len(cat_rows):
        issues.append({"check": "Row count", "status": "PASS",
                        "detail": f"{len(cat_rows)} rows (matches source)"})
    else:
        issues.append({"check": "Row count", "status": "FAIL",
                        "detail": f"Source: {len(source_rows)}, Output: {len(cat_rows)}"})

    # 2. Missing department
    missing_dept = [r["Vendor Name"] for r in cat_rows if not r.get("Department")]
    if missing_dept:
        issues.append({"check": "Missing Department", "status": "FAIL",
                        "detail": f"{len(missing_dept)} vendors: {', '.join(missing_dept[:5])}{'…' if len(missing_dept)>5 else ''}"})
    else:
        issues.append({"check": "Missing Department", "status": "PASS", "detail": "All vendors have a department"})

    # 3. Invalid department values
    invalid_dept = [
        f"{r['Vendor Name']} -> \"{r['Department']}\""
        for r in cat_rows
        if r.get("Department") and r["Department"] not in VALID_DEPARTMENTS
    ]
    if invalid_dept:
        issues.append({"check": "Invalid Department values", "status": "FAIL",
                        "detail": f"{len(invalid_dept)} vendors: {'; '.join(invalid_dept[:5])}{'…' if len(invalid_dept)>5 else ''}"})
    else:
        issues.append({"check": "Invalid Department values", "status": "PASS",
                        "detail": f"All departments are from the approved list"})

    # 4. Missing description
    missing_desc = [r["Vendor Name"] for r in cat_rows if not r.get("1-line Description on what the Vendor does")]
    if missing_desc:
        issues.append({"check": "Missing Description", "status": "FAIL",
                        "detail": f"{len(missing_desc)} vendors: {', '.join(missing_desc[:5])}{'…' if len(missing_desc)>5 else ''}"})
    else:
        issues.append({"check": "Missing Description", "status": "PASS", "detail": "All vendors have a description"})

    # 5. Description length
    short = [r["Vendor Name"] for r in cat_rows
             if r.get("1-line Description on what the Vendor does")
             and len(r["1-line Description on what the Vendor does"]) < 10]
    long_ = [r["Vendor Name"] for r in cat_rows
              if r.get("1-line Description on what the Vendor does")
              and len(r["1-line Description on what the Vendor does"]) > 180]
    if short or long_:
        detail = ""
        if short:
            detail += f"{len(short)} too short (<10 chars). "
        if long_:
            detail += f"{len(long_)} too long (>180 chars)."
        issues.append({"check": "Description length (10–180 chars)", "status": "WARN", "detail": detail.strip()})
    else:
        desc_lens = [len(r.get("1-line Description on what the Vendor does", "")) for r in cat_rows]
        avg = sum(desc_lens) / len(desc_lens) if desc_lens else 0
        issues.append({"check": "Description length (10–180 chars)", "status": "PASS",
                        "detail": f"All within range. Avg length: {avg:.0f} chars"})

    # 6. Generic descriptions
    generic_vendors = [
        f"{r['Vendor Name']}: \"{r['1-line Description on what the Vendor does']}\""
        for r in cat_rows
        if is_generic(r.get("1-line Description on what the Vendor does", ""))
    ]
    if generic_vendors:
        issues.append({"check": "Generic descriptions", "status": "WARN",
                        "detail": f"{len(generic_vendors)} potentially generic: " +
                                  "; ".join(generic_vendors[:3]) + ("…" if len(generic_vendors) > 3 else "")})
    else:
        issues.append({"check": "Generic descriptions", "status": "PASS",
                        "detail": "No obvious generic phrases detected"})

    return issues


def claude_quality_check(client, rows: list[dict]) -> tuple[list[dict], str]:
    """Sample descriptions and ask Claude to rate specificity."""
    # Stratified sample: pick proportionally from each dept
    by_dept: dict[str, list] = {}
    for r in rows:
        d = r.get("Department", "UNCLASSIFIED")
        by_dept.setdefault(d, []).append(r)

    sample = []
    per_dept = max(1, SAMPLE_SIZE // len(by_dept))
    for dept, dept_rows in by_dept.items():
        chosen = random.sample(dept_rows, min(per_dept, len(dept_rows)))
        sample.extend(chosen)
    sample = sample[:SAMPLE_SIZE]

    items_str = "\n".join(
        f'{i+1}. Vendor: "{r["Vendor Name"]}" | Dept: {r["Department"]}\n'
        f'   Description: "{r["1-line Description on what the Vendor does"]}"'
        for i, r in enumerate(sample)
    )

    prompt = f"""You are a quality reviewer auditing vendor descriptions for a VP of Operations report.

Review each description below. For each:
1. Rate specificity: GOOD, ACCEPTABLE, or WEAK
2. If WEAK or ACCEPTABLE, suggest a short improved version (≤120 chars)

Criteria:
- GOOD: Clearly states the product category and use case (e.g., "E-signature platform for contract signing workflows")
- ACCEPTABLE: Reasonably specific but could be more precise
- WEAK: Generic, vague, or could apply to hundreds of companies

Return ONLY a valid JSON array, no markdown. Each element:
{{
  "vendor": "<vendor name>",
  "rating": "GOOD" | "ACCEPTABLE" | "WEAK",
  "suggestion": "<improved description or empty string if GOOD>"
}}

DESCRIPTIONS TO REVIEW:
{items_str}"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        raw = raw.rsplit("```", 1)[0].strip()

    ratings = json.loads(raw)
    return ratings, items_str


# ---------------------------------------------------------------------------
def main():
    print("=== Step 2: Validate Categorization ===\n")

    client = anthropic.Anthropic()

    if not CATEGORIZED_CSV.exists():
        print(f"ERROR: {CATEGORIZED_CSV} not found. Run step1_categorize.py first.")
        sys.exit(1)

    source_rows = load_csv(SOURCE_CSV)
    cat_rows = load_csv(CATEGORIZED_CSV)

    # --- Structural checks ---
    print("Running structural checks…")
    struct_issues = structural_checks(source_rows, cat_rows)
    for issue in struct_issues:
        icon = {"PASS": "[OK]", "FAIL": "[X]", "WARN": "[!]"}.get(issue["status"], "?")
        print(f"  {icon} [{issue['status']}] {issue['check']}: {issue['detail']}")

    # --- Claude quality check ---
    print(f"\nRunning Claude description quality check on {SAMPLE_SIZE} sampled vendors…")
    ratings, _ = claude_quality_check(client, cat_rows)

    good = [r for r in ratings if r["rating"] == "GOOD"]
    acceptable = [r for r in ratings if r["rating"] == "ACCEPTABLE"]
    weak = [r for r in ratings if r["rating"] == "WEAK"]

    print(f"  GOOD: {len(good)} | ACCEPTABLE: {len(acceptable)} | WEAK: {len(weak)}")
    if weak:
        print("  Weak descriptions flagged:")
        for w in weak:
            print(f"    • {w['vendor']}: {w.get('suggestion', '(no suggestion)')}")

    # --- Write Markdown report ---
    total = len(cat_rows)
    pass_count = sum(1 for i in struct_issues if i["status"] == "PASS")
    fail_count = sum(1 for i in struct_issues if i["status"] == "FAIL")
    warn_count = sum(1 for i in struct_issues if i["status"] == "WARN")

    overall = "PASS" if fail_count == 0 else "FAIL"

    md_lines = [
        "# Validation Report — Vendor Categorization",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Source:** `vendors_categorized.csv` ({total} vendors)  ",
        f"**Overall Result:** {'✅ PASS' if overall == 'PASS' else '❌ FAIL'}",
        "",
        "---",
        "",
        "## 1. Structural Checks",
        "",
        "| Check | Status | Detail |",
        "|-------|--------|--------|",
    ]
    for issue in struct_issues:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "[!]️"}.get(issue["status"], "?")
        md_lines.append(f"| {issue['check']} | {icon} {issue['status']} | {issue['detail']} |")

    md_lines += [
        "",
        f"**Summary:** {pass_count} passed, {warn_count} warnings, {fail_count} failed",
        "",
        "---",
        "",
        "## 2. Claude Description Quality Check",
        "",
        f"**Sample size:** {len(ratings)} vendors (stratified by department)  ",
        f"**GOOD:** {len(good)} | **ACCEPTABLE:** {len(acceptable)} | **WEAK:** {len(weak)}",
        "",
    ]

    if weak:
        md_lines += [
            "### Weak Descriptions (require improvement)",
            "",
            "| Vendor | Current Description | Suggested Improvement |",
            "|--------|--------------------|-----------------------|",
        ]
        for w in weak:
            current = next(
                (r.get("1-line Description on what the Vendor does", "") for r in cat_rows
                 if r["Vendor Name"] == w["vendor"]), ""
            )
            md_lines.append(f"| {w['vendor']} | {current} | {w.get('suggestion', '')} |")
        md_lines.append("")

    if acceptable:
        md_lines += [
            "### Acceptable Descriptions (could be improved)",
            "",
            "| Vendor | Suggestion |",
            "|--------|------------|",
        ]
        for a in acceptable:
            if a.get("suggestion"):
                md_lines.append(f"| {a['vendor']} | {a['suggestion']} |")
        md_lines.append("")

    md_lines += [
        "### Good Descriptions (sample)",
        "",
        "| Vendor | Description |",
        "|--------|-------------|",
    ]
    for g in good[:10]:
        current = next(
            (r.get("1-line Description on what the Vendor does", "") for r in cat_rows
             if r["Vendor Name"] == g["vendor"]), ""
        )
        md_lines.append(f"| {g['vendor']} | {current} |")

    md_lines += [
        "",
        "---",
        "",
        "## 3. Validation Criteria",
        "",
        "| Criterion | Rule |",
        "|-----------|------|",
        "| Row count | Output must match source (384 vendors) |",
        "| Department | Must be one of 12 approved departments |",
        "| Description presence | Every vendor must have a description |",
        "| Description length | 10–180 characters |",
        "| Description quality | No generic phrases; Claude-rated ≥ ACCEPTABLE |",
        "",
        "_Generated by `scripts/step2_validate.py`_",
    ]

    VALIDATION_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nValidation report saved -> {VALIDATION_MD}")
    print("\n[OK] Step 2 complete. Run step3_recommend.py next.")


if __name__ == "__main__":
    main()
