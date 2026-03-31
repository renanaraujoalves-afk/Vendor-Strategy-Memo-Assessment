# Part 3 — Methodology
**Date:** 2026-03-31
**Project:** Vendor Strategy Memo Assessment
**Role:** VP of Operations (acquired company, ~$1B ARR)

---

## 1. Approach

The work was organized into four sequential parts, each building on the previous output:

| Part | Task | Approach |
|------|------|----------|
| 1 | Vendor Classification & Recommendations | Python scripts calling the Anthropic API in batches |
| 2 | Top 3 Strategic Opportunities | Claude Code native analysis (no script) |
| 3 | Methodology (this document) | Synthesized from git history and prompt logs |
| 4 | Executive Memo | Claude Code skill composition + Node.js docx export |

All scripts were saved in `scripts/`, all outputs in `outputs/`. Each step was wrapped in a Claude Code slash command (`.claude/commands/`) to be repeatable.

---

## 2. Tools Used

| Tool | Purpose |
|------|---------|
| **Claude Code CLI** | Orchestration, file I/O, slash command execution |
| **Anthropic Python SDK** | API calls for classification and validation (Steps 1–3) |
| **`claude-sonnet-4-6`** | Vendor categorization and description quality review |
| **`claude-opus-4-6`** | Strategic recommendations (higher reasoning requirement) |
| **Python 3** | Structural validation, batching, CSV manipulation |
| **Node.js + `docx` npm** | Word document generation for the executive memo |
| **`executive-briefing` skill** | BLUF-format memo content composition |
| **`docx` skill** | docx-js workflow for professional Word output |

---

## 3. Prompts Created

### Prompt 1 — Vendor Categorization (`step1_categorize.py`)
Model: `claude-sonnet-4-6` · Batches: 7 × 60 vendors

Each vendor was sent with its name and annual spend. The prompt required the model to return a valid JSON array with `vendor`, `department` (from a strict approved list of 12), and `description` (≤120 chars, specific — not generic). Example of the specificity guidance given:

> Good: "European cloud telephony platform for customer support call routing"
> Bad: "Business services provider"

### Prompt 2 — Description Quality Review (`step2_validate.py`)
Model: `claude-sonnet-4-6` · Sample: 34 vendors (stratified by department)

A second model call rated each description as **GOOD / ACCEPTABLE / WEAK** and suggested improvements for anything below GOOD. The 3 weak descriptions identified were corrected directly in the CSV before proceeding.

### Prompt 3 — Strategic Recommendations (`step3_recommend.py`)
Model: `claude-opus-4-6` · Batches: 8 × 50 vendors

Each vendor was classified as **Terminate / Consolidate / Optimize** based on explicit guidelines: spend threshold ($5K floor for Terminate), functional overlap rules for Consolidate, and strategic necessity / renegotiation potential for Optimize. Eight assumptions were encoded directly in the prompt (insurance = Optimize, completed Professional Services = Terminate, etc.).

### Prompt 4 — Top 3 Opportunities (`/step5-opportunities` command)
No API script — Claude Code read `vendors_final.csv` and `pivot_summary.csv` directly and performed the analysis natively, ranking opportunities by absolute USD savings potential.

### Prompt 5 — Executive Memo (`/step6-executive-memo` command)
Orchestrated via two skills: `executive-briefing` (BLUF format, CEO/CFO audience) and `docx` (professional Word export). All data in the memo came from prior outputs — no placeholders.

---

## 4. Validation & Quality Checks

### Structural Checks (automated — `step2_validate.py`)

| Check | Result |
|-------|--------|
| Row count matches source | PASS — 386 rows |
| All departments from approved list | PASS — 12 valid departments |
| No missing departments | PASS |
| No missing descriptions | PASS |
| Description length 10–180 chars | PASS — avg 80 chars |
| Generic phrase detection | WARN — 53 flagged for manual review |

Full report: [`outputs/validation_categorization.md`](validation_categorization.md)

### Description Quality Check (AI-assisted — Claude sample review)

A stratified sample of 34 vendors (across all departments) was reviewed by the model:

| Rating | Count |
|--------|-------|
| GOOD | 23 |
| ACCEPTABLE | 8 |
| WEAK | 3 |

The 3 weak descriptions (Trending Technology Services GmbH, Fabiola Thistlewhaite, Advena) were corrected in the CSV before recommendations were generated.

### Recommendation Audit (human review — `step4_audit.py`)

Two audit samples were generated and reviewed by the human auditor (VP of Operations):

| Sample | Selection | Vendors | Spend Coverage |
|--------|-----------|---------|----------------|
| Top spend | Top 5% by 12-month spend | 19 vendors | $5.8M / 74% of total |
| Random | 5% random from remaining | 19 vendors | — |

**Auditor feedback:** No corrections noted. All recommendations accepted as-is.

Full report: [`outputs/validation_recommendations.md`](validation_recommendations.md)

---

## 5. Issues Encountered & Resolved

| Issue | Resolution |
|-------|-----------|
| 3 vendors with non-ASCII characters (Croatian: č, š, đ) failed API response matching | Fixed with substring matching and direct CSV patching |
| Windows cp1252 encoding errors on Unicode print symbols | Added `sys.stdout.reconfigure(encoding="utf-8")` to all scripts |
| Node.js not found on PATH (nvm4w installed but no active version) | User installed Node.js; session resumed |
| `docx` npm package not globally available | Resolved with `npm install docx` locally in the project directory |

---

*Generated from git history and session logs in `claude-prompts-history/`*