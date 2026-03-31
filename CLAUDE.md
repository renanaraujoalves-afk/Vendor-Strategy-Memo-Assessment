# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a **Vendor Strategy Memo Assessment** project. The goal is to act as VP of Operations for an acquired company, analyze ~400 vendors and their last 12 months of spend, and produce a C-suite executive memo with cost-saving recommendations.

### Deliverables
1. **Vendor Analysis** — Classify each vendor by Department, add a 1-line description, and assign a recommendation: `Terminate`, `Consolidate`, or `Optimize`.
2. **Top 3 Opportunities** — The three highest-impact savings opportunities with title, explanation, and estimated annual savings.
3. **Methodology** — Approach, tools, prompts, and quality-check evidence.
4. **Executive Memo** — 1-page C-suite memo (CEO/CFO) with findings, savings, timeline, implementation, and risks.

## Key Files

| File | Purpose |
|---|---|
| `inputs/Vendor Analysis Assessment.csv` | Source data: ~400 vendors with 12-month spend |
| `inputs/Config.csv` | Valid department names to use for classification |
| `outputs/` | Generated outputs go here |
| `scripts/` | Scripts used for processing go here |
| `tasks/Assignment.md` | Full task brief |

## Department Classifications

Use only the departments from `inputs/Config.csv`

## Skills Available

### `/executive-briefing`
Use when writing the executive memo. Follow the BLUF (Bottom Line Up Front) format defined in `.claude/skills/executive-briefing/SKILL.md`.

### `/docx` (document creation)
Use when exporting the executive memo to `.docx`. See `.claude/skills/docx/SKILL.md` for the full workflow

## Evaluation Criteria

The submission is evaluated on:
- Accurate department classification
- Concise, specific vendor descriptions (not generic like "business services provider")
- Realistic and strategic recommendations with risk factors
- Top 3 opportunities that are financially justified and significant enough for a ~$1B business
- Documented methodology and quality-check evidence
- Executive memo: clear formatting, no errors, actionable savings
- Well-organized project folder with inputs, outputs, scripts, and a README
