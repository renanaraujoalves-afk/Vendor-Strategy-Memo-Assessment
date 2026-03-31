# Step 5 — Identify Top 3 Strategic Opportunities (Part 2)

Read `outputs/vendors_final.csv` and `outputs/pivot_summary.csv`, then identify the three highest-impact cost-saving opportunities and write the results to `outputs/top3_opportunities.md`.

## Instructions

1. Read both source files:
   - `outputs/vendors_final.csv` — full vendor list with Department, Spend, Description, Recommendation, and Rationale
   - `outputs/pivot_summary.csv` — department-level spend rollup

2. Analyze the data, prioritizing:
   - Largest absolute USD savings potential
   - Consolidation opportunities where multiple vendors serve the same function
   - Termination clusters where many small vendors can be cut en masse
   - Optimization opportunities for top-spend vendors with renegotiation leverage

3. Each opportunity must include:
   - **Title** — short, action-oriented (e.g., "CRM Spend Consolidation")
   - **Explanation** — 2–4 sentences describing what the opportunity is, which vendors are involved, and why it's actionable
   - **Estimated Annual Savings (USD)** — a conservative but financially justified estimate with brief rationale

4. Write the output to `outputs/top3_opportunities.md` using this structure:

```markdown
# Top 3 Strategic Cost-Saving Opportunities

_Analysis based on ~400 vendors and $X total annual spend_

---

## Opportunity 1: [Title]

**Estimated Annual Savings: $X,XXX,XXX**

[Explanation paragraph]

**Vendors involved:** Vendor A ($X), Vendor B ($X), ...

---

## Opportunity 2: [Title]

**Estimated Annual Savings: $X,XXX,XXX**

[Explanation paragraph]

**Vendors involved:** Vendor A ($X), Vendor B ($X), ...

---

## Opportunity 3: [Title]

**Estimated Annual Savings: $X,XXX,XXX**

[Explanation paragraph]

**Vendors involved:** Vendor A ($X), Vendor B ($X), ...

---

_Total Estimated Annual Savings: $X,XXX,XXX_
```

## After completing the analysis

1. Confirm `outputs/top3_opportunities.md` was created
2. Display the full contents of the file to the user
3. Summarize the three opportunities in one sentence each, and state the total combined estimated savings
4. Tell the user to run `/executive-briefing` next for Part 4
