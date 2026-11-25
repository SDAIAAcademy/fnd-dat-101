# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 2.1 · Questions 5 to 7: bands and sets
#
# Day 2 · Session 1 (CASE expressions and set operations) · 30 min.
#
# Three more of the twenty questions: two need a CASE expression, one a set operation. Predict
# first, then query. The answers go to `answers/part2.sql`.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Write a prediction for each of the three questions · 4 min
# - [ ] Question 5: order lines in quantity bands · 8 min
# - [ ] Question 6: paid and free delivery per order status · 8 min
# - [ ] Question 7: January customers who did not order in June · 7 min
# - [ ] Save the part file · 3 min
# - [ ] ✱ Stretch · Answer question 7 again with NOT EXISTS and confirm both give the same count

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
con = U.db()

# %% [markdown]
# ## 1 · Predictions first · 4 min
#
# Open `data/twenty_questions.md`. ✏️ Write one line per question: how many rows, roughly what
# value, or what the first row will be. Then answer the questions below.

# %%
PRED_Q05 = """
-- BEGIN SOLUTION
three rows; single the largest band, many the smallest
-- END SOLUTION
"""
PRED_Q06 = """
-- BEGIN SOLUTION
three rows; most delivered orders paid no fee
-- END SOLUTION
"""
PRED_Q07 = """
-- BEGIN SOLUTION
one number, a few thousand customers
-- END SOLUTION
"""

# %% [markdown]
# ## 2 · Bands, conditional counts and a set · 23 min

# %% [markdown]
# **Question 5.** How many order lines fall in each quantity band: `single` (1), `few` (2 or 3), `many` (4 or more)?
# Columns `band, lines`.

# %%
SQL_Q05 = """
-- BEGIN SOLUTION
SELECT CASE WHEN quantity = 1 THEN 'single'
            WHEN quantity <= 3 THEN 'few'
            ELSE 'many' END AS band,
       COUNT(*) AS lines
FROM order_lines
GROUP BY band
-- END SOLUTION
"""
U.check("q05", SQL_Q05)

# %% [markdown]
# **Question 6.** For each order status, how many orders paid a delivery fee and how many did not? Columns
# `status, paid, free`. Count with a CASE inside `SUM`, or with `COUNT(*) FILTER (WHERE ...)`.

# %%
SQL_Q06 = """
-- BEGIN SOLUTION
SELECT status,
       SUM(CASE WHEN delivery_fee > 0 THEN 1 ELSE 0 END) AS paid,
       SUM(CASE WHEN delivery_fee = 0 THEN 1 ELSE 0 END) AS free
FROM orders
GROUP BY status
-- END SOLUTION
"""
U.check("q06", SQL_Q06)

# %% [markdown]
# **Question 7.** How many customers placed an order in January 2026 but none in June 2026? One column,
# `customers`. Build two lists of customer ids and take one away from the other with `EXCEPT`.

# %%
SQL_Q07 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS customers
FROM (
  SELECT customer_id FROM orders
  WHERE ordered_at >= DATE '2026-01-01' AND ordered_at < DATE '2026-02-01'
  EXCEPT
  SELECT customer_id FROM orders
  WHERE ordered_at >= DATE '2026-06-01' AND ordered_at < DATE '2026-07-01'
)
-- END SOLUTION
"""
U.check("q07", SQL_Q07)

# %% [markdown]
# **Look at** UNION against UNION ALL: the first removes duplicate rows, the second keeps them.
# Run the cell: the same customers ordered in both months many times over.

# %%
U.show("""SELECT (SELECT COUNT(*) FROM (SELECT customer_id FROM orders WHERE ordered_at < DATE '2026-02-01' UNION SELECT customer_id FROM orders WHERE ordered_at >= DATE '2026-06-01')) AS union_rows,
       (SELECT COUNT(*) FROM (SELECT customer_id FROM orders WHERE ordered_at < DATE '2026-02-01' UNION ALL SELECT customer_id FROM orders WHERE ordered_at >= DATE '2026-06-01')) AS union_all_rows""")

# %% [markdown]
# ## 3 · Save the part file · 3 min

# %%
U.save_part("part2", {"q05": (PRED_Q05, SQL_Q05), "q06": (PRED_Q06, SQL_Q06), "q07": (PRED_Q07, SQL_Q07)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. In question 5, why does the order of the WHEN branches matter?</summary>
#
# CASE takes the first branch that is true. With `quantity <= 3` first, a quantity of 1 would be "few".
# </details>
#
# <details><summary>2. Why does question 7 need EXCEPT on customer ids, not on whole order rows?</summary>
#
# EXCEPT compares whole rows. Order rows of January and June never match, so nothing would be taken away.
# </details>
#
# <details><summary>3. What does EXCEPT do with a customer who ordered ten times in January?</summary>
#
# Set operations work on distinct rows: the customer counts once.
# </details>
#
# **Carry forward**: `answers/part2.sql`, read by the checker in lab 3.2.
