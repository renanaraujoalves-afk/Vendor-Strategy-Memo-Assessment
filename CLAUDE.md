# CLAUDE.md

Act as **VP of Operations** for an acquired company. Analyze ~400 vendors (12-month spend) and produce C-suite cost-saving recommendations.

## Key References

| Path | Purpose |
|---|---|
| `tasks/Assignment.md` | Full task brief and evaluation criteria |
| `inputs/Vendor Analysis Assessment.csv` | Source vendor data |
| `inputs/Config.csv` | Valid department names (use only these) |
| `outputs/` | All generated outputs |
| `scripts/` | Processing scripts |

## Workflow Skills (slash commands)

| Command | When to use |
|---|---|
| `/step1-categorize_vendors` | Classify vendors by department + 1-line description |
| `/step2-validate_vendors_categorization` | Validate categorization output |
| `/step3-recommend_actions_on_vendors` | Assign Terminate / Consolidate / Optimize |
| `/step4-audit_vendor_data_analysis` | Audit sample for human review |
| `/step5-recommend_3_opportunities` | Identify top 3 savings opportunities |
| `/step6-generate_executive_memo` | Draft the C-suite executive memo |
| `/executive-briefing` | Format memo in BLUF style |
| `/docx` | Export memo to `.docx` |
