# Step 1 — Categorize Vendors (Department + Description)

Run the categorization script to assign each vendor a Department and 1-line Description using Claude, then generate a spend pivot table by department.

```bash
python scripts/step1_categorize_vendors.py
```

After the script completes:
1. Confirm the output was saved to `outputs/vendors_categorized.csv`
2. Read and display the pivot table from `outputs/pivot_summary.txt`
3. Highlight the top 3 departments by spend and note any vendors left UNCLASSIFIED
4. Tell the user to run `/step2-validate_vendors_categorization` next
