# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 2.2 · Predict, then run: twelve NULL comparisons
#
# Day 2 · Session 2 (NULL and three-valued logic) · 35 min.
#
# Twelve short queries on the printed mini tables. You predict what each returns on paper,
# with the assistant off, then run them and mark yourself. Then you repair three queries so they
# say what was meant. This is the kind of reasoning the timed check on the capstone day asks for.
#
# AI policy: AI-off for the predictions. In the repairs, an assistant may explain an error
# message; it does not write the query.
#
# **Tasks**
# - [ ] Print the mini customers and order lines · 3 min
# - [ ] Predict the row count of each of the twelve queries on paper · 12 min
# - [ ] Run the twelve and mark each prediction · 8 min
# - [ ] Rewrite three queries so they say what was meant · 9 min
# - [ ] Write the NULL rule you will keep · 3 min
# - [ ] ✱ Stretch · Show NOT IN returning no rows when the list holds a NULL, and the NOT EXISTS that does not

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/fnd-dat-101.git"
    if not Path("/content/fnd-dat-101").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/fnd-dat-101"], check=True)
    os.chdir("/content/fnd-dat-101/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("_tools").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())
import sqllab as U
m = U.mini()  # the six mini tables, in memory

# %% [markdown]
# ## 1 · The printed tables · 3 min
#
# Print them, or copy them onto paper. Close the assistant.

# %%
U.show("SELECT customer_id, region FROM customers", m)
U.show("SELECT order_id, line_no, quantity, unit_price, discount FROM order_lines", m, n=20)

# %% [markdown]
# ## 2 · Twelve predictions · 12 min
#
# For each query, predict the single number it prints. Write it after the bar in the cell
# below, one line per query, before you run anything.
#
# | # | Query |
# |---|---|
# | n01 | `SELECT COUNT(*) FROM customers WHERE region = 'North'` |
# | n02 | `SELECT COUNT(*) FROM customers WHERE region <> 'North'` |
# | n03 | `SELECT COUNT(*) FROM customers WHERE region = NULL` |
# | n04 | `SELECT COUNT(*) FROM customers WHERE region IS NULL` |
# | n05 | `SELECT COUNT(*) FROM customers WHERE NOT (region = 'North')` |
# | n06 | `SELECT COUNT(*) FROM customers WHERE region <> 'North' OR region IS NULL` |
# | n07 | `SELECT COUNT(*) FROM customers WHERE region IS DISTINCT FROM 'North'` |
# | n08 | `SELECT COUNT(*) FROM customers WHERE region NOT IN ('North', NULL)` |
# | n09 | `SELECT COUNT(*) FROM order_lines WHERE discount > 0` |
# | n10 | `SELECT COUNT(*) FROM order_lines WHERE discount = 0` |
# | n11 | `SELECT COUNT(*) FROM order_lines WHERE COALESCE(discount, 0) = 0` |
# | n12 | `SELECT COUNT(discount) FROM order_lines` |

# %%
QUERIES = {
    "n01": "SELECT COUNT(*) FROM customers WHERE region = 'North'",
    "n02": "SELECT COUNT(*) FROM customers WHERE region <> 'North'",
    "n03": "SELECT COUNT(*) FROM customers WHERE region = NULL",
    "n04": "SELECT COUNT(*) FROM customers WHERE region IS NULL",
    "n05": "SELECT COUNT(*) FROM customers WHERE NOT (region = 'North')",
    "n06": "SELECT COUNT(*) FROM customers WHERE region <> 'North' OR region IS NULL",
    "n07": "SELECT COUNT(*) FROM customers WHERE region IS DISTINCT FROM 'North'",
    "n08": "SELECT COUNT(*) FROM customers WHERE region NOT IN ('North', NULL)",
    "n09": "SELECT COUNT(*) FROM order_lines WHERE discount > 0",
    "n10": "SELECT COUNT(*) FROM order_lines WHERE discount = 0",
    "n11": "SELECT COUNT(*) FROM order_lines WHERE COALESCE(discount, 0) = 0",
    "n12": "SELECT COUNT(discount) FROM order_lines",
}

# %% [markdown]
# ✏️ **Exercise 1** · Your predictions, one per line: the query number, a bar, the number.

# %%
PREDICTIONS = """
-- BEGIN SOLUTION
n01 | 2
n02 | 2
n03 | 0
n04 | 2
n05 | 2
n06 | 4
n07 | 4
n08 | 0
n09 | 2
n10 | 1
n11 | 12
n12 | 3
-- END SOLUTION
"""

# %% [markdown]
# ## 3 · Run and mark · 8 min

# %%
right = U.mark_predictions(PREDICTIONS, QUERIES, m)

# %% [markdown]
# **Look at** the ones you missed. Most misses fall in two groups: a comparison with NULL that
# you expected to be true (n02, n05, n08), and a NULL you expected to count as zero (n10, n12).
#
# ## 4 · Say what was meant · 9 min
#
# ✏️ **Exercise 2** · The data protection officer asks for every customer who is not in the
# North, **including** those whose region is missing. Return the count as `customers`.

# %%
SQL_2 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS customers
FROM customers
WHERE region IS DISTINCT FROM 'North'
-- END SOLUTION
"""
U.check("l22_not_north", SQL_2, con=m)

# %% [markdown]
# ✏️ **Exercise 3** · Finance asks how many lines had no discount: an empty discount and a
# discount of 0.00 both mean none. Return `lines`.

# %%
SQL_3 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS lines
FROM order_lines
WHERE COALESCE(discount, 0) = 0
-- END SOLUTION
"""
U.check("l22_no_discount", SQL_3, con=m)

# %% [markdown]
# ✏️ **Exercise 4** · The average discount per line, where an empty discount counts as 0.
# Return `avg_discount`. (`AVG(discount)` alone skips the empty ones: compare the two.)

# %%
SQL_4 = """
-- BEGIN SOLUTION
SELECT AVG(COALESCE(discount, 0)) AS avg_discount
FROM order_lines
-- END SOLUTION
"""
U.check("l22_avg_discount", SQL_4, con=m)
U.show("SELECT AVG(discount) AS skips_nulls, AVG(COALESCE(discount, 0)) AS counts_nulls_as_zero FROM order_lines", m)

# %% [markdown]
# ## 5 · The rule you keep · 3 min
#
# ✏️ Write one sentence you will remember, in your own words.

# %%
RULE = """
-- BEGIN SOLUTION
A comparison with NULL is unknown, and WHERE keeps only true rows: ask IS NULL, or COALESCE first.
-- END SOLUTION
"""
print(RULE)

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why does n02 not count the two customers without a region?</summary>
#
# For them, `region <> 'North'` is unknown, not true. WHERE keeps only rows where the condition
# is true.
# </details>
#
# <details><summary>2. Why does n08 return 0?</summary>
#
# `region NOT IN ('North', NULL)` means `region <> 'North' AND region <> NULL`. The second part
# is unknown for every row, so the whole condition is never true.
# </details>
#
# <details><summary>3. When is AVG(discount) the right answer?</summary>
#
# When the question is the average among lines that had a discount recorded. When an empty
# discount means "none", the question wants the zeros in: use COALESCE.
# </details>
#
# **Carry forward**: nothing; lab 2.3 starts from the company's database.
