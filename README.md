# Vendor Strategy Memo Assessment

A Claude Code-driven vendor spend analysis for an acquired company (~$1B ARR). Acting as VP of Operations, this project analyzes ~400 vendors across 12 months of spend, classifies them by department, generates strategic recommendations, and produces a C-suite executive memo.

**Total vendor spend analyzed:** $7,887,359  
**Identified savings opportunities:** ~$905,000/year

---

## How It Was Built

The project follows a six-step pipeline, each wrapped as a repeatable Claude Code slash command under `.claude/commands/`.

### Step 1 — Classify Vendors (`/step1-categorize_vendors`)

Runs `scripts/step1_categorize_vendors.py`, which reads the source CSV and calls `claude-sonnet-4-6` in batches of 60 vendors. Each vendor is assigned:
- A **department** from the approved list in `inputs/Config.csv`
- A **specific one-line description** (generic phrases like "business services provider" are explicitly rejected by the prompt)

Output: `outputs/vendors_categorized.csv`

### Step 2 — Validate Categorization (`/step2-validate_vendors_categorization`)

Runs `scripts/step2_validate_vendors_categorization.py`, which performs:
- **Structural checks** (row count, valid departments, missing values, description length)
- **AI-assisted quality review** on a stratified sample of 34 vendors — rated GOOD / ACCEPTABLE / WEAK
- 3 weak descriptions were corrected before proceeding

Output: `outputs/validation_categorization.md`

### Step 3 — Strategic Recommendations (`/step3-recommend_actions_on_vendors`)

Runs `scripts/step3_recommend_actions_on_vendors.py` using `claude-opus-4-6` in batches of 50 vendors. Each vendor receives one of:
- **Terminate** — no longer needed (enforced $5K spend floor)
- **Consolidate** — functional overlap with another vendor
- **Optimize** — useful but opportunity to reduce cost or renegotiate

Eight business rules were encoded in the prompt (e.g., insurance = Optimize, completed Professional Services = Terminate).

Output: `outputs/vendors_final.csv`

### Step 4 — Audit Sample (`/step4-audit_vendor_data_analysis`)

Runs `scripts/step4_audit_vendor_data_analysis.py`, which generates two audit samples:
- Top 5% by spend (19 vendors, covering 74% of total spend)
- Random 5% of remaining vendors (19 vendors)

These were reviewed by the human auditor (VP of Operations). No corrections were required.

Output: `outputs/validation_recommendations.md`

### Step 5 — Top 3 Opportunities (`/step5-recommend_3_opportunities`)

Claude Code read `vendors_final.csv` and `pivot_summary.csv` directly (no API script) and identified the three highest-impact savings opportunities ranked by absolute USD potential:

1. **Salesforce CRM License Audit & Renegotiation** — $500K/year
2. **Croatia & Global Facilities Vendor Consolidation** — $245K/year
3. **Finance & Audit Advisory Rationalization** — $160K/year

Output: `outputs/top3_opportunities.md`

### Step 6 — Executive Memo (`/step6-generate_executive_memo`)

Composed using two Claude Code skills:
- `executive-briefing` — BLUF (Bottom Line Up Front) format, CEO/CFO audience
- `docx` — professional Word export via `scripts/generate_executive_memo.js`

All figures in the memo come from prior outputs — no placeholders.

Output: `outputs/Executive Memo.docx`

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python 3 | 3.9+ |
| `anthropic` Python SDK | `pip install anthropic` |
| Node.js | 18+ |
| `docx` npm package | `npm install` (in project root) |
| `ANTHROPIC_API_KEY` | Set in `.env` or environment |

Install Node.js dependencies:

```bash
npm install
```

---

## Running the Pipeline

Each step can be run via its Claude Code slash command (requires Claude Code CLI) or directly:

```bash
# Step 1 — Categorize vendors
python scripts/step1_categorize_vendors.py

# Step 2 — Validate categorization
python scripts/step2_validate_vendors_categorization.py

# Step 3 — Assign recommendations
python scripts/step3_recommend_actions_on_vendors.py

# Step 4 — Generate audit samples
python scripts/step4_audit_vendor_data_analysis.py

# Step 6 — Export executive memo to Word
node scripts/generate_executive_memo.js
```

Steps 5 and 6 (opportunities analysis and memo writing) are driven by Claude Code directly and do not require standalone scripts.


---
## Methodology Description
### Tools Decision
At my work, if this assignment was a one-time task, I would use Gemini embedded tools or Antigravity to perform it directly in G Workspace. However, since it was requested to build with Claude CLI, I assumed this assignment was recurrent, meaning it was better to build a Claude project with tools that can be reused or even expanded later by the team. Therefore, I chose to structure a Claude Code project on git which used commands and python scripts to perform the tasks in sequence, always giving feedback to the user.

### Project Development
First, I analyzed the entire assignment and sketched on paper and through conversations with Gemini the structure I chose to work with, using commands and python scripts. Then, I created a folder, opened with VSCode, added the essential Claude Skills I intended to use and created the git repo. 

At a real project, I would have started by adding either Google Workspace CLI or creating python scripts to work directly with the original Google Sheets through automation. Since those approaches depend on company policies due to security concerns, and demands an initial setup in Google Cloud Platform, I decided to simplify for this project and work with .csv, which was manually exported from G Sheets and later imported back to paste the results.

Then, the process followed a four-step sequential approach orchestrated by the Claude Code CLI, on which I used the prompting for each part, did a quick review of the plan, commands and scripts and iterated with the agent. I preferred to use Python scripts to handle the core data processing, choosing to use claude-sonnet-4-6 for tasks like categorization and claude-opus-4-6 for higher-level strategic reasoning. Node.js and the docx package were then utilized to export the Executive Memo directly in docx. Each step was encapsulated in repeatable slash commands to ensure consistency from data ingestion to the final output.

### Workflow Methodology
The core workflow began by batch-processing vendor data through the Sonnet model to assign approved departments and generate precise, concise descriptions. After validating the quality of these descriptions, the script used Opus model to apply strict financial thresholds and business rules to classify each vendor’s status as either Terminate, Consolidate, or Optimize. Then, I used the IDE with Opus to analyze the processed dataset to rank the top three highest-value savings opportunities, culminating in the generation of the Word document.

### Validation and Quality Assurance
QA was performed during the vendor data analysis with care, since all subsequent tasks depended on it. The QA process was built with automated structural checks for data integrity with python, AI-assisted sample reviews of the vendor descriptions with Opus API, and a final human audit by the user (me). Minor technical hurdles were systematically resolved through Claude CLI. All the evidence of the QA validations were stored in the outputs folder of the git repo. The top 3 opportunities and the Executive Memo were both proof read manually for strategic validation by me, using especially the generated pivot table in git as a base, however, I only did minor adjustments.

### Prompts and Detailed Methodology
All prompts history after the start of the project were stored in the git repo for archive. The only prompts not stored were the ones with Gemini Pro to discuss the approaches before starting. Check also the "methodology" markdown file in git for complete methodology.


---

## Deliverables

| Part | File |
|---|---|
| Part 1 — Vendor Analysis | `outputs/vendors_final.csv` |
| Part 2 — Top 3 Opportunities | `outputs/top3_opportunities.md` |
| Part 3 — Methodology | `outputs/methodology.md` |
| Part 4 — Executive Memo | `outputs/Executive Memo.docx` |

---

*Built entirely with Claude Code CLI using `claude-sonnet-4-6` and `claude-opus-4-6`.*
