# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 3.3 · Window drills 1: top items per region
#
# Day 3 · Session 3 (Partitions, ranking, lag and lead) · 30 min.
#
# Window functions compute over a set of related rows and keep every row. You rank products
# within each region, compare the three ranking functions where values tie, and measure the days
# between a customer's orders. Write one comment line per drill that starts `-- partition:` and
# says what the partition is and why: the checker of lab 3.4 requires it. The drills are saved to
# `answers/windows1.sql`.
#
# AI policy: an assistant may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Drill 1: the top three products per region by quantity · 10 min
# - [ ] Drill 2: ROW_NUMBER, RANK and DENSE_RANK on the same ties · 6 min
# - [ ] Drill 3: days since the customer's previous order, with LAG · 8 min
# - [ ] Write the partition comments and save the drills · 6 min
# - [ ] ✱ Stretch · Return the top three per region with QUALIFY and with a subquery, and confirm they agree

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
# ## 1 · Drill 1: the top three products per region · 10 min
#
# For each store region, the three products with the most units sold (quantity of `ok` lines of
# `delivered` orders), ranked with `RANK()`, so ties share a place. Columns
# `region, product_id, units, place`, by region, then place, then `product_id`.

# %%
SQL_W1 = """
-- BEGIN SOLUTION
-- partition: one ranking per store region, so each region gets its own places 1, 2, 3
WITH units AS (
  SELECT s.region, l.product_id, SUM(l.quantity) AS units
  FROM order_lines l
  JOIN orders o ON o.order_id = l.order_id
  JOIN stores s ON s.store_id = o.store_id
  WHERE o.status = 'delivered' AND l.line_status = 'ok'
  GROUP BY s.region, l.product_id
),
ranked AS (
  SELECT region, product_id, units,
         RANK() OVER (PARTITION BY region ORDER BY units DESC) AS place
  FROM units
)
SELECT region, product_id, units, place
FROM ranked
WHERE place <= 3
ORDER BY region, place, product_id
-- END SOLUTION
"""
U.check("w1", SQL_W1)

# %% [markdown]
# A window cannot be filtered in the WHERE of the same query: the ranking is computed after
# WHERE. Rank in one step, filter in the next, as above, or use `QUALIFY` (the stretch).

# %% [markdown]
# ## 2 · Drill 2: three ranking functions on the same ties · 6 min
#
# The ten most expensive Bakery products, with `ROW_NUMBER()`, `RANK()` and `DENSE_RANK()` over
# `list_price` from the highest. Columns `product_id, list_price, rn, rk, drk`, by `rn`. For
# `rn`, break ties by `product_id` so the numbering is the same on every run.

# %%
SQL_W2 = """
-- BEGIN SOLUTION
-- partition: none; the whole Bakery category is one window ordered by price
SELECT product_id, list_price,
       ROW_NUMBER() OVER (ORDER BY list_price DESC, product_id) AS rn,
       RANK()       OVER (ORDER BY list_price DESC) AS rk,
       DENSE_RANK() OVER (ORDER BY list_price DESC) AS drk
FROM products
WHERE category = 'Bakery'
ORDER BY rn
LIMIT 10
-- END SOLUTION
"""
U.check("w2", SQL_W2)

# %% [markdown]
# **Look at** the rows where two prices tie: `rn` keeps counting, `rk` repeats and then skips,
# `drk` repeats and does not skip.

# %% [markdown]
# ## 3 · Drill 3: days since the previous order · 8 min
#
# For every order of customers C00010 and C00011: the days since that customer's previous
# order, with `LAG`. Columns `customer_id, order_id, order_date, days_since_previous`, by
# customer, then date, then order. The first order of each customer has no previous one.

# %%
SQL_W3 = """
-- BEGIN SOLUTION
-- partition: one sequence per customer, so LAG never reaches into another customer's orders
SELECT customer_id, order_id,
       CAST(ordered_at AS DATE) AS order_date,
       CAST(ordered_at AS DATE)
         - LAG(CAST(ordered_at AS DATE)) OVER (PARTITION BY customer_id ORDER BY ordered_at, order_id)
         AS days_since_previous
FROM orders
WHERE customer_id IN ('C00010', 'C00011')
ORDER BY customer_id, order_date, order_id
-- END SOLUTION
"""
U.check("w3", SQL_W3)

# %% [markdown]
# **Look at** the first row of the second customer: without `PARTITION BY customer_id`, LAG would
# measure from the other customer's last order.

# %% [markdown]
# ## 4 · Save the drills · 6 min
#
# Check that each query starts with its `-- partition:` comment, then save.

# %%
U.save_part("windows1", {"w1": ("", SQL_W1), "w2": ("", SQL_W2), "w3": ("", SQL_W3)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why does drill 1 use RANK and not ROW_NUMBER?</summary>
#
# With ROW_NUMBER, two products tied on units would get different places by chance, and one could drop out of the top three.
# </details>
#
# <details><summary>2. What does PARTITION BY change in a window, and what does it not change?</summary>
#
# It restarts the computation for each group; it does not reduce the rows. GROUP BY does that.
# </details>
#
# <details><summary>3. Why is days_since_previous NULL in the first row of each customer?</summary>
#
# LAG has no earlier row in that partition, so it returns NULL.
# </details>
#
# **Carry forward**: `answers/windows1.sql`, read by the window checker in lab 3.4.
