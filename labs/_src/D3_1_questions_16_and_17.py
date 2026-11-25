# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 3.1 · Questions 16 and 17: count once
#
# Day 3 · Session 1 (Join fan-out and double counting) · 35 min.
#
# A join from order lines to delivery attempts repeats every line once per attempt. You watch
# a sum grow, then answer two questions that need lines and attempts together without counting
# anything twice. The answers go to `answers/part5.sql`.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Count rows before and after joining delivery attempts · 6 min
# - [ ] Write a prediction for each of the two questions · 4 min
# - [ ] Question 16: line value of orders that needed a second attempt · 10 min
# - [ ] Question 17: orders and attempts per store in one result · 10 min
# - [ ] Save the part file · 5 min
# - [ ] ✱ Stretch · Find the share by which the naive sum of line values overstates the true one

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
# ## 1 · See the fan-out · 6 min
#
# Count the order lines, then count the rows after joining each line to its order's delivery
# attempts. Then compare two sums of line value.

# %%
U.show("""
SELECT (SELECT COUNT(*) FROM order_lines) AS lines,
       (SELECT COUNT(*) FROM order_lines l JOIN deliveries d ON d.order_id = l.order_id) AS lines_joined_to_attempts
""")

# %% [markdown]
# ✏️ **Exercise 1** · Sum `quantity * unit_price` over all order lines (`naive_sum` after the join
# to `deliveries`), and over the lines alone (`true_sum`). Return both in one row.

# %%
SQL_FAN = """
-- BEGIN SOLUTION
SELECT (SELECT SUM(l.quantity * l.unit_price) FROM order_lines l JOIN deliveries d ON d.order_id = l.order_id) AS naive_sum,
       (SELECT SUM(quantity * unit_price) FROM order_lines) AS true_sum
-- END SOLUTION
"""
U.check("l31_fanout", SQL_FAN)

# %% [markdown]
# **Look at** the two sums. The join is wrong twice over: it repeats every line of an order
# that needed a second or third attempt, and it drops every line of an order that never had
# an attempt. The naive sum is not even wrong by a fixed amount.
#
# ## 2 · Predictions · 4 min
#
# ✏️ Write one line for each of questions 16 and 17.

# %%
PRED_Q16 = """
-- BEGIN SOLUTION
one number, a few million riyals
-- END SOLUTION
"""
PRED_Q17 = """
-- BEGIN SOLUTION
eight rows; attempts a little above orders in every store
-- END SOLUTION
"""

# %% [markdown]
# ## 3 · Questions 16 and 17 · 20 min

# %% [markdown]
# **Question 16.** What is the total line value (quantity times unit price, lines with status ok) of the orders
# that needed more than one delivery attempt? Count each line once. One column, `line_value`.
# Find the orders first, then sum their lines: never sum across the join to `deliveries`.

# %%
SQL_Q16 = """
-- BEGIN SOLUTION
SELECT SUM(l.quantity * l.unit_price) AS line_value
FROM order_lines l
WHERE l.line_status = 'ok'
  AND l.order_id IN (
    SELECT order_id FROM deliveries GROUP BY order_id HAVING COUNT(*) > 1
  )
-- END SOLUTION
"""
U.check("q16", SQL_Q16)

# %% [markdown]
# **Question 17.** For each store: how many orders had at least one delivery attempt, and how many attempts were
# made? Columns `store_id, orders, attempts`, by `store_id`.

# %%
SQL_Q17 = """
-- BEGIN SOLUTION
SELECT o.store_id,
       COUNT(DISTINCT o.order_id) AS orders,
       COUNT(*) AS attempts
FROM orders o
JOIN deliveries d ON d.order_id = o.order_id
GROUP BY o.store_id
ORDER BY o.store_id
-- END SOLUTION
"""
U.check("q17", SQL_Q17)

# %% [markdown]
# ## 4 · Save the part file · 5 min
#
# Before saving, write the grain of each table your two queries read, as a comment above each query.

# %%
U.save_part("part5", {"q16": (PRED_Q16, SQL_Q16), "q17": (PRED_Q17, SQL_Q17)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. In question 17, why is COUNT(*) right for attempts but wrong for orders?</summary>
#
# After the join there is one row per attempt. COUNT(*) counts attempts; orders need COUNT(DISTINCT order_id).
# </details>
#
# <details><summary>2. Would question 16 be right with a join to deliveries and SUM(DISTINCT ...)?</summary>
#
# No: two different lines with the same value would collapse into one. Filter the orders first, then sum.
# </details>
#
# <details><summary>3. Which grain does the result of question 16 have?</summary>
#
# One row in all: a single total over lines, each counted once.
# </details>
#
# **Carry forward**: `answers/part5.sql`, read by the checker in lab 3.2.
