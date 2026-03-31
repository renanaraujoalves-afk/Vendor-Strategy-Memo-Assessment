# Part 2 — Claude Prompts & Session Summary
**Date:** 2026-03-31  
**Project:** Vendor Strategy Memo Assessment  
**Role:** VP of Operations (acquired company, ~$1B ARR)

---

## Session Summary

This session covered Part 2 of the assignment — identifying the three highest-impact strategic cost-saving opportunities from the vendor dataset produced in Part 1. Rather than using a Python script, Claude Code read the data directly and performed the analysis natively, writing the output as a structured Markdown file.

### What was built

One Claude Code slash command (`.claude/commands/step5-opportunities.md`) was created to run Part 2 as a self-contained, repeatable command. The command was designed and refined before execution.

### What Claude did, step by step

| Step | Action | Output |
|------|--------|--------|
| 1 | Created `/step5-opportunities` command with Opus model + Python script | `.claude/commands/step5-opportunities.md` (v1) |
| 2 | User requested simplification: removed Python script dependency and model reference | `.claude/commands/step5-opportunities.md` (v2, final) |
| 3 | Read `outputs/vendors_final.csv` (386 vendors) and `outputs/pivot_summary.csv` | — |
| 4 | Analyzed spend distribution, identified Consolidate/Terminate clusters, and ranked by savings potential | — |
| 5 | Wrote structured Markdown report with 3 opportunities, vendor details, and savings estimates | `outputs/top3_opportunities.md` |

### Opportunities identified

| # | Title | Key Vendors | Est. Annual Savings |
|---|-------|-------------|-------------------|
| 1 | Salesforce CRM License Audit & Contract Renegotiation | Salesforce UK ($3.1M), HubSpot ($32K) | $500,000 |
| 2 | Croatia & Global Facilities Vendor Consolidation | Zagrebtower ($183K), Weking ($144K), 40+ tail vendors | $245,000 |
| 3 | Finance & Audit Advisory Rationalization | Grant Thornton ($46K), Harmonic Group ($65K), Sage UK ($46K) | $160,000 |
| | **Total** | | **$905,000** |

### Analytical approach

- **Opportunity 1** was identified by spend concentration: Salesforce alone = 39.5% of total spend, making it the single highest-leverage renegotiation target. The 15% savings estimate is conservative for a contract of this size; seat audits at scale routinely uncover 20–30% waste.
- **Opportunity 2** was identified by vendor fragmentation: 122 vendors for $1.2M in Facilities is an extreme ratio (~$10K/vendor average). The Zagreb office duplication (two separate Croatian office leases) was the most impactful single action within the cluster.
- **Opportunity 3** was identified by functional overlap: multiple audit, tax, and advisory firms operating in parallel alongside a duplicative FP&A platform, creating consolidation potential without capability loss.

---

## The `/step5-opportunities` Command

**File:** `.claude/commands/step5-opportunities.md`  
**Execution:** Claude reads CSVs directly and performs analysis natively (no Python script)  
**Output:** `outputs/top3_opportunities.md`

The command instructs Claude to:
1. Read both source files (`vendors_final.csv` and `pivot_summary.csv`)
2. Prioritize opportunities by: largest absolute USD savings, consolidation clusters, termination tail, and renegotiation leverage
3. Write a Markdown report in a fixed structure (title, explanation, estimated savings, vendors involved)
4. Display results and point to `/executive-briefing` as next step

---

## User Prompts to Claude Code (this session)

**1.**
> Create a claude command that performs the part 2 of the assignment, meaning to Identify Strategic Opportunities, outlining:
> - The three highest-impact recommendations based on vendor data
> - Each should include:
>   - A summary title (e.g., "CRM Tool Consolidation")
>   - A brief explanation
>   - An estimated annual savings in USD
>
> These opportunities should be evaluated based on the "vendors_final.csv" and "pivot_summary.csv", using Opus model. The output should be a .md file in the folder "outputs"

**2.**
> Remove the python script to simplify and remove the recommendation of using the **claude-opus-4-6** model, I will select the model in the terminal myself

**3.**
> Now run it for me

**4.**
> Now summarize the prompts and results of this session and add as: "assignment_part2_prompts" in folder "claude-prompts-history"
