# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 3.2 · Questions 18 to 20, and the checker
#
# Day 3 · Session 2 (Subqueries and common table expressions) · 35 min.
#
# The last three questions need answers built in steps: a subquery, then common table
# expressions. Question 19 follows the finance rule, which is not in the schema. Then the
# automatic checker reads all your part files and scores the twenty. This file is assessed:
# 16 of 20 is the mark the outcome asks for.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Write a prediction for each of the three questions · 4 min
# - [ ] Question 18: products above their category's average price · 8 min
# - [ ] Question 19: net revenue by month of delivery, by the finance rule · 9 min
# - [ ] Question 20: the five customers with the highest net revenue · 8 min
# - [ ] Run the checker over all your part files and fix one failure · 6 min
# - [ ] ✱ Stretch · Rewrite question 19 as one query without common table expressions and compare how easy each is to check

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
PRED_Q18 = """
-- BEGIN SOLUTION
eight rows, about half of each category above its average
-- END SOLUTION
"""
PRED_Q19 = """
-- BEGIN SOLUTION
seven rows: January to June, and a small July from orders delivered after 30 June
-- END SOLUTION
"""
PRED_Q20 = """
-- BEGIN SOLUTION
five rows, the top customer a few thousand riyals
-- END SOLUTION
"""

# %% [markdown]
# ## 2 · Three answers in steps · 25 min
#
# Run each step of a chain on its own before you trust the last line: select from the first
# common table expression alone, look at a few rows, then add the next.

# %% [markdown]
# **Question 18.** In each category, how many products have a list price above the average list price of their
# own category? Leave out products without a category. Columns `category, products`, by `category`.

# %%
SQL_Q18 = """
-- BEGIN SOLUTION
WITH avg_price AS (
  SELECT category, AVG(list_price) AS avg_list_price
  FROM products
  WHERE category IS NOT NULL
  GROUP BY category
)
SELECT p.category, COUNT(*) AS products
FROM products p
JOIN avg_price a ON a.category = p.category
WHERE p.list_price > a.avg_list_price
GROUP BY p.category
ORDER BY p.category
-- END SOLUTION
"""
U.check("q18", SQL_Q18)

# %% [markdown]
# **Question 19.** What was the net revenue in each month, by the finance rule (`data/revenue_rule.md`)? Columns
# `month, net_revenue`, the month as its first day, by `month`. Build it in named steps: the
# delivery date of each order, the revenue of each line, then the months.

# %%
SQL_Q19 = """
-- BEGIN SOLUTION
WITH delivered AS (            -- one row per delivered order: the date of its successful attempt
  SELECT d.order_id, CAST(d.attempted_at AS DATE) AS delivered_on
  FROM deliveries d
  JOIN orders o ON o.order_id = d.order_id
  WHERE d.outcome = 'delivered' AND o.status = 'delivered'
),
line_revenue AS (             -- one row per order line that counts
  SELECT l.order_id, l.quantity * l.unit_price - COALESCE(l.discount, 0) AS revenue
  FROM order_lines l
  WHERE l.line_status = 'ok'
)
SELECT CAST(date_trunc('month', dv.delivered_on) AS DATE) AS month,
       ROUND(SUM(lr.revenue), 2) AS net_revenue
FROM line_revenue lr
JOIN delivered dv ON dv.order_id = lr.order_id
GROUP BY month
ORDER BY month
-- END SOLUTION
"""
U.check("q19", SQL_Q19)

# %% [markdown]
# **Question 20.** Which five customers brought the most net revenue by the finance rule, and how many delivered
# orders did each have? Columns `customer_id, net_revenue, delivered_orders`, by net revenue from
# the highest.

# %%
SQL_Q20 = """
-- BEGIN SOLUTION
WITH line_revenue AS (
  SELECT l.order_id, SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS revenue
  FROM order_lines l
  WHERE l.line_status = 'ok'
  GROUP BY l.order_id
)
SELECT o.customer_id,
       ROUND(SUM(lr.revenue), 2) AS net_revenue,
       COUNT(*) AS delivered_orders
FROM orders o
JOIN line_revenue lr ON lr.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY o.customer_id
ORDER BY net_revenue DESC
LIMIT 5
-- END SOLUTION
"""
U.check("q20", SQL_Q20)

# %% [markdown]
# ## 3 · Save, then run the checker · 6 min

# %%
U.save_part("part6", {"q18": (PRED_Q18, SQL_Q18), "q19": (PRED_Q19, SQL_Q19), "q20": (PRED_Q20, SQL_Q20)})

# %%
score = U.grade_twenty()

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. In question 19, what would change if the month came from ordered_at?</summary>
#
# Orders placed late on the last day of a month and delivered the next day would move back a month, and the July row would vanish.
# </details>
#
# <details><summary>2. Why does question 20 sum line revenue per order before joining to orders?</summary>
#
# It keeps the grain clear: one row per order on each side of the join, so nothing is repeated.
# </details>
#
# <details><summary>3. The checker reports a missing question from Day 1. What do you do?</summary>
#
# Run that day's notebook again: it writes its part file into answers/.
# </details>
#
# **Carry forward**: the twenty answers in `answers/part1.sql` to `answers/part6.sql`: the assessed query file.
