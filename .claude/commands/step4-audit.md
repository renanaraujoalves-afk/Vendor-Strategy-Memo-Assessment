# Step 4 — Audit Sample for Human Review

Run the audit script to surface the top 5% vendors by spend and a random 5% sample for manual review.

```bash
python scripts/step4_audit.py
```

The script will:
1. Print the **top 5% by spend** (~19 vendors) — highest financial risk if miscategorized
2. Print a **random 5% sample** (~19 vendors) — statistical coverage of the rest
3. Prompt you interactively to enter corrections in the format:
   ```
   <Vendor Name> | <Correct Recommendation> | <Note>
   ```
   Type `done` when finished reviewing.

After the script completes:
1. Read `outputs/validation_recommendations.md` and summarize the audit findings
2. If corrections were logged, list them and confirm they should be applied to `vendors_final.csv`
3. If corrections exist, apply them to `outputs/vendors_final.csv` using the Edit tool
4. Confirm that Part 1 is complete and both validation reports are in the `outputs/` folder
5. Summarize what was produced:
   - `outputs/vendors_final.csv` — complete vendor dataset with recommendations
   - `outputs/validation_categorization.md` — Step 2 quality report
   - `outputs/validation_recommendations.md` — Step 4 audit report
