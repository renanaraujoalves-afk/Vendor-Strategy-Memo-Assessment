# Step 2 — Validate Categorization

Run the validation script to check structural integrity and description quality of the categorized vendor data.

```bash
python scripts/step2_validate_vendors_categorization.py
```

After the script completes:
1. Read `outputs/validation_categorization.md` and summarize the results
2. Call out any FAIL or WARN items specifically — list the affected vendor names
3. If there are WEAK descriptions, display Claude's suggested improvements
4. Recommend whether to proceed or fix issues first before moving to Step 3
5. If all checks pass, tell the user to run `/step3-recommend_actions_on_vendors` next
