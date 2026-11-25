# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 2.4 · Questions 12 to 15: joins
#
# Day 2 · Session 4 (Inner, outer, semi and anti joins) · 35 min.
#
# Four questions, one for each kind of join: inner, left, anti and semi. Predict, then query.
# The answers go to `answers/part4.sql`.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Write a prediction for each of the four questions · 5 min
# - [ ] Question 12: delivered orders per store region · 7 min
# - [ ] Question 13: customers and never-ordered customers per region · 8 min
# - [ ] Question 14: active products that were never sold · 7 min
# - [ ] Question 15: customers with at least one failed attempt · 5 min
# - [ ] Save the part file · 3 min
# - [ ] ✱ Stretch · Write question 13 with a left join and with NOT EXISTS, and say which one a reader understands first

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
# ## 1 · Predictions first · 5 min
#
# Open `data/twenty_questions.md`. ✏️ Write one line per question: how many rows, roughly what
# value, or what the first row will be. Then answer the questions below.

# %%
PRED_Q12 = """
-- BEGIN SOLUTION
five rows of similar size, about 45,000 orders each
-- END SOLUTION
"""
PRED_Q13 = """
-- BEGIN SOLUTION
six rows: five regions and none; about one customer in five never ordered
-- END SOLUTION
"""
PRED_Q14 = """
-- BEGIN SOLUTION
a short list of products with no line at all
-- END SOLUTION
"""
PRED_Q15 = """
-- BEGIN SOLUTION
one number, over ten thousand customers
-- END SOLUTION
"""

# %% [markdown]
# ## 2 · Four joins · 27 min

# %% [markdown]
# **Question 12.** How many delivered orders came from the stores of each region? Columns `region, orders`, by
# `region`. The region of a store is in `stores`.

# %%
SQL_Q12 = """
-- BEGIN SOLUTION
SELECT s.region, COUNT(*) AS orders
FROM orders o
JOIN stores s ON s.store_id = o.store_id
WHERE o.status = 'delivered'
GROUP BY s.region
ORDER BY s.region
-- END SOLUTION
"""
U.check("q12", SQL_Q12)

# %% [markdown]
# **Question 13.** For each customer region, with `none` where the region is missing: how many customers, and
# how many of them never ordered? Columns `region, customers, never_ordered`, by `region`.
# A customer who never ordered has no row in `orders`: a `LEFT JOIN` keeps them.

# %%
SQL_Q13 = """
-- BEGIN SOLUTION
SELECT COALESCE(c.region, 'none') AS region,
       COUNT(DISTINCT c.customer_id) AS customers,
       COUNT(DISTINCT CASE WHEN o.order_id IS NULL THEN c.customer_id END) AS never_ordered
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY COALESCE(c.region, 'none')
ORDER BY region
-- END SOLUTION
"""
U.check("q13", SQL_Q13)

# %% [markdown]
# **Question 14.** Which products are listed as active but were never sold? Columns `product_id, product_name`,
# by `product_id`. An anti join: keep the products for which no order line exists.

# %%
SQL_Q14 = """
-- BEGIN SOLUTION
SELECT p.product_id, p.product_name
FROM products p
WHERE p.is_active
  AND NOT EXISTS (SELECT 1 FROM order_lines l WHERE l.product_id = p.product_id)
ORDER BY p.product_id
-- END SOLUTION
"""
U.check("q14", SQL_Q14)

# %% [markdown]
# **Question 15.** How many customers had at least one order with a failed delivery attempt? One column,
# `customers`. A semi join keeps each customer once, however many failures they had.

# %%
SQL_Q15 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS customers
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN deliveries d ON d.order_id = o.order_id
  WHERE o.customer_id = c.customer_id AND d.outcome = 'failed'
)
-- END SOLUTION
"""
U.check("q15", SQL_Q15)

# %% [markdown]
# ## 3 · Save the part file · 3 min

# %%
U.save_part("part4", {"q12": (PRED_Q12, SQL_Q12), "q13": (PRED_Q13, SQL_Q13), "q14": (PRED_Q14, SQL_Q14), "q15": (PRED_Q15, SQL_Q15)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. In question 13, why COUNT(DISTINCT c.customer_id) and not COUNT(*)?</summary>
#
# After the left join a customer appears once per order. COUNT(*) would count orders, not customers.
# </details>
#
# <details><summary>2. Why is NOT EXISTS safer than NOT IN for question 14?</summary>
#
# If the subquery ever returned a NULL, NOT IN would keep no row at all. NOT EXISTS is not affected by NULLs.
# </details>
#
# <details><summary>3. What would an inner join of customers to failed attempts count in question 15?</summary>
#
# One row per failed attempt: a customer with three failures would count three times.
# </details>
#
# **Carry forward**: `answers/part4.sql`, read by the checker in lab 3.2.
