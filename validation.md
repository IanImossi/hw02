Complete this table in `hw02/validation.md`. Every row must be filled in.

| Check | Expected | Your Script Produced | Match? | Notes |
|---|---|---|---|---|
| Dataset shape | (298772, 9) | Shape Check: OK (matches expcted (298772, 9)) | Yes | While it was not an exact match in wording, the validation did check if the file was (298772, 9) |
| Null count — `security_id` | 101,597 | security_id   101597 | Yes | Did find all of the null security_id but did not use a comma |
| Null count — `amount` | 0 | amount             0 | Yes | Found 0 nulls in amount |
| Unique `txn_type` values | 6 | Unique txn_type values: 6 | Yes | Matched |
| Count of `Buy` transactions | 83,556 | Buy           83556 | Yes | Did not include comma |
| `txn_date` data type | object | txn_date stored as: object | Yes | Matched |
| Earliest `txn_date` | 2020-01-01 |Earliest txn_date:  2020-01-01 | Yes | Matched |
| Latest `txn_date` | 2024-12-30 |Latest txn_date:    2024-12-30 | Yes | Matched |
| Duplicate `txn_id` count | 0 | Duplicate txn_id values: 0 | Yes | Matched |
| Mean `amount` | $54,075.17 | Mean amount:     $54,075.17 | Yes | Matched with dollar signs, decimal, and comma |
| Median `amount` | $41,220.48 | Median amount:   $41,220.49 | Yes | Matched with dollar signs, decimal, and comma |
| Skewness of `amount` | 1.15 | Skewness:        1.15 (right-skewed) | Yes | Matched with which type of skewedness |
| Correlation `shares`–`amount` | 0.65 | 0.65 | Yes | Matched |
| Correlation `price`–`amount` | 0.64 |  0.64 | Yes | Matched |
| Correlation `shares`–`price` | 0.00 | 0.00 | Yes | Matched |
| Negative `shares` count (Buy only) | 836 | Total negative shares rows: 836 | Yes | Matched number |
| Profile file created | Yes | Yes | | |
| Chart files created (3) | Yes | Yes | | |

For any row where Match = No: describe the discrepancy and paste the Claude Cowork conversation you used to investigate it.

---

### 2B — Explain the Code and Output (16 points)

Open a **new** Claude Cowork session — not the one that generated the script. In that session, send two prompts in sequence.

**Prompt 1 (the code):** Paste your complete `hw02_eda.py` script and ask:

> *"Walk me through each section of this script, including the grouping, correlation, and charting steps. What should I see in the terminal when I run it? List each expected output value explicitly."*

**Prompt 2 (the output):** Paste your complete terminal output — all lines, not just the summary numbers — and ask:

> *"Here is the terminal output from running an EDA script on a wealth management transaction dataset. What does each value mean? Flag anything that looks unexpected or that I should investigate before using this data in an analysis."*

In `hw02/validation.md`, answer:

1. Did Claude's predicted outputs (from Prompt 1) match what you actually saw in the terminal? List any discrepancies.
- The format of the Claude output matched what the terminal in VS Code printed out. However, since Claude did not have the raw data, it was unable to fill in the answers for the table.

2. What did Claude flag as potentially unexpected or worth investigating (from Prompt 2)?
- Claude flagged numerous portions of the terminal output. It saw that 836 buy rows have negative shares. Dividend amounts looked unrealistic. The advisory fee was heavily skewed. That amount matches shares x price. The date edges and transactions on weekends. For example there were transactions on New Years Day. There were fractional sales. There is a Matplotlib deprecation warning

3. Did Claude mention the 101,597 null values in `security_id`? What explanation did it give?
- Initially, Claude did not mention the null values. Upon asking, Claude claimed that the null values are likely not errors as they are non applicable values. 

4. Did Claude flag the `txn_date` column as a concern? Why would that matter for a time-series analysis?
- Claude did flag dates as a potential issue because there are some transactions on some holidays and weekends. For example, New Years Day has transactions, but New Years Eve does not. It is inconsistent that some holidays and weekends have transactions but others do not, which could skew a time-series analysis.

5. Open your three chart files. Does what you see in each image match Claude's explanation of that section of the output? Note any differences.
- Claude mostly described the three images. However, in scatter_shares_amount.png, Claude poorly described what the image should show. Instead of saying triangles, Claude uses "fans" and only described seeing the blue "fan" on the negative side and did not indicate well that there was a mostly green triangle on the positive side.

6. Paste one follow-up question you asked Claude, and Claude's answer.
- Why is there no section 1 in the terminal output?

- Section 1 is in the code but never gets a header. Loading the data is step 1, labeled only by the comment # 1. Load data. That block never calls section(1, ...), so the first printed header is 2.

### 2C — Business Check & Cross-Validation (16 points)

**Business-reasonableness questions.** Apply your knowledge of Wildcat Capital's business. Answer each question in your own words in `hw02/validation.md` — do not paste Claude's response as your answer here.

1. `security_id`, `shares`, and `price` are all null in exactly 101,597 rows. Looking at the `txn_type` value counts, which three transaction types would you expect to have no security — and why? Do the counts add up to 101,597?
- The three transaction types that would not have a security are deposit, withdrawal and advisory fee. This is because no investment is being bought or sold. It matches up with the missing 101,597 with deposit having 35,981, withdrawal having 35,766, and advisory fee having 29,850 transactions.

2. There are 83,556 Buy transactions and 59,755 Sell transactions. What does it mean for a wealth management firm to have significantly more Buys than Sells over a five-year period?
- It suggests that the clients are net accumulators as they put more money into assets rather than selling them off.

3. The `txn_date` column is stored as a string (type `object`) rather than a date. If Claude Cowork generated code to compute the average number of days between transactions, what would go wrong if the dates remained as strings?
- The string variable type cannot be computed as Python does not recognize the numbers in the dates as numbers. Therefore the object varible type must be used in order for Python to recognize the dates as numbers.

4. Wildcat Capital has 2,700 clients served by 25 advisors. Is that ratio — roughly 108 clients per advisor — plausible for a registered investment advisory firm?
- It is plausible, although it would be considered the upper limit of what that many advisors can do. A comfortable range for the number of clients an advisor can take on is 50-150 according to https://smartasset.com/advisor-resources/average-number-of-clients-per-financial-advisor.

5. 836 `Buy` transactions have negative `shares` values (as low as −499.63), while every other transaction type in the dataset has only positive share values. What are two plausible business explanations for a negative share count on a Buy transaction (for example, a data-entry sign error versus a legitimate correction or reversal entry), and what would you do next to determine which explanation is more likely?
- There could be a data entry or system sign error. Also there could be entry corrections. A script can created to look for entry corrections in which for every negative buy, in the days preceeding, check for a positive version. If there is none, it is likely an error.

For any question where you are uncertain, use Claude Cowork: *"Is [observation] typical for a wealth management firm? Cite a source."*

> *You do not need to know Python to recognize that three non-trade transaction types would logically have no associated security.*

> *Investigate outliers and anomalies before deciding whether to exclude them — an unexplained pattern is a finding, not automatically an error.*

**Cross-validation.** The count of `Buy` transactions (83,556) is a central metric in any portfolio activity analysis. Verify it using two independent approaches:

- **Prompt A:** *"Write Python to count rows in fact_transactions.csv where txn_type equals exactly 'Buy'."*
- **Prompt B:** *"Write Python to count the total rows in fact_transactions.csv, then subtract the count of rows where txn_type is Sell, Deposit, Withdrawal, Dividend, or Advisory Fee."*

Run both scripts from the VS Code terminal. In `hw02/validation.md`:

6. What did each script return?
- Prompt A - Rows where txn_type == Buy: 83,556

- Prompt B - Total rows: 298,772
Other types: 215,216
Remainder: 83,556

7. Do the results agree? If not, which one is wrong and why?
- The results agree because the remainder of prompt B can only equal the Buy rows

8. Why is it useful to verify a count using subtraction rather than direct filtering?
- It is useful to verify counts using subtraction because it shows null values that could otherwise be mislabeled Buy rows.