# Step 3 — Strategic Recommendations

Run the recommendation script to assign Terminate / Consolidate / Optimize to each vendor using explicit guidelines and assumptions.

**Guidelines applied by the script:**
- **Terminate**: Spend < $5K/yr with no strategic value, redundant/duplicate tools, completed one-time engagements
- **Consolidate**: Multiple vendors serving the same function (e.g., two CRM tools, multiple cloud storage)
- **Optimize**: Strategically necessary vendors with cost-reduction opportunities; default when uncertain

**Key assumptions:**
- Company has ~$1B ARR; $5K/yr is the Terminate threshold for unclear vendors
- Insurance, legal, compliance vendors → Optimize by default
- Engineering infra (cloud, CDN, monitoring) → Optimize
- Duplicate SaaS tools in same category → Consolidate (smaller spend vendor flagged first)

```bash
python scripts/step3_recommend.py
```

After the script completes:
1. Read `outputs/vendors_final.csv` and summarize the recommendation breakdown (counts + spend by recommendation)
2. Highlight the top 5 Terminate candidates (lowest spend, clearest rationale)
3. Highlight the top 3 Consolidate opportunities (highest combined savings potential)
4. Note any vendors with "uncertain" or weak rationale that may need manual review
5. Tell the user to run `/step4-audit` next
