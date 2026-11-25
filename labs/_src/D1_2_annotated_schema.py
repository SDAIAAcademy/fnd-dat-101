# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 1.2 · The annotated schema
#
# Day 1 · Session 2 (Grain and cardinality) · 35 min.
#
# You write down what one row of each table stands for (its grain) and its key, then prove each
# claim with a counting query. You measure how many rows of one table meet one row of another.
# The result is the annotated schema of the six tables: it is checked against the reference and
# is part of your assessed work.
#
# AI policy for this lab: an assistant may explain an error message to you; it does not write
# your queries or your schema notes.
#
# **Tasks**
# - [ ] Write the grain of each table in one sentence · 6 min
# - [ ] Confirm each grain with a counting query · 10 min
# - [ ] Measure lines per order, attempts per order and orders per customer · 10 min
# - [ ] Fill in the annotated schema and run its check · 9 min
# - [ ] ✱ Stretch · List every join of the schema that can multiply rows, and the column that causes it

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
# ## 1 · The grain in one sentence · 6 min
#
# The grain is what one row stands for: "one order", "one line of one order", "one attempt to
# deliver one order". Write it for each table in the annotated schema of task 4 now, before you
# count; the counts of task 2 will confirm or correct you.
#
# ## 2 · Confirm a grain by counting · 10 min
#
# If the grain of `orders` is "one order", then `order_id` never repeats. If the grain of
# `deliveries` is "one attempt", then the pair `(order_id, attempt_no)` never repeats.
#
# ✏️ **Exercise 1** · Return the number of rows of `deliveries` and the number of distinct
# pairs `(order_id, attempt_no)`, as `n_rows` and `n_attempts`.

# %%
SQL_1 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n_rows,
       (SELECT COUNT(*) FROM (SELECT DISTINCT order_id, attempt_no FROM deliveries)) AS n_attempts
FROM deliveries
-- END SOLUTION
"""
U.check("l12_attempt_grain", SQL_1)

# %% [markdown]
# ✏️ **Exercise 2** · The grain of `customers` is "one customer". Confirm it: rows and distinct
# `customer_id`, as `n_rows` and `n_customers`.

# %%
SQL_2 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n_rows, COUNT(DISTINCT customer_id) AS n_customers FROM customers
-- END SOLUTION
"""
U.check("l12_customer_grain", SQL_2)

# %% [markdown]
# ## 3 · Cardinality: how many meet one · 10 min
#
# Group the many side by the key of the one side and look at the smallest and largest group.
# Here is the pattern for lines per order:

# %%
U.show("""
SELECT MIN(n) AS fewest, MAX(n) AS most
FROM (SELECT order_id, COUNT(*) AS n FROM order_lines GROUP BY order_id)
""")

# %% [markdown]
# ✏️ **Exercise 3** · Attempts per order: the most attempts any order had. Return one number,
# `most`.

# %%
SQL_3 = """
-- BEGIN SOLUTION
SELECT MAX(n) AS most
FROM (SELECT order_id, COUNT(*) AS n FROM deliveries GROUP BY order_id)
-- END SOLUTION
"""
U.check("l12_attempts_max", SQL_3)

# %% [markdown]
# Grouping `deliveries` only finds orders that have attempts. Some orders have none.
#
# ✏️ **Exercise 4** · How many orders have no row at all in `deliveries`? Return `n`.

# %%
SQL_4 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n
FROM orders
WHERE order_id NOT IN (SELECT order_id FROM deliveries)
-- END SOLUTION
"""
U.check("l12_orders_without_attempt", SQL_4)

# %% [markdown]
# ✏️ **Exercise 5** · Orders per customer: the fewest and the most, counted over **all**
# customers, including those who never ordered. Return `fewest` and `most`.
# Hint: count orders per customer in a subquery, then think about the customers it misses.

# %%
SQL_5 = """
-- BEGIN SOLUTION
SELECT MIN(n) AS fewest, MAX(n) AS most
FROM (SELECT c.customer_id, COUNT(o.order_id) AS n
      FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
      GROUP BY c.customer_id)
-- END SOLUTION
"""
U.check("l12_orders_per_customer", SQL_5)

# %% [markdown]
# A `LEFT JOIN` keeps customers without orders; you will meet it properly on Day 2. Without it,
# the fewest would read 1 and hide every customer who never ordered.
#
# ✏️ **Exercise 6** · Lines per product over **all** products: the most lines any product has.
# Return `most`. (The fewest is 0: some products never sold.)

# %%
SQL_6 = """
-- BEGIN SOLUTION
SELECT MAX(n) AS most
FROM (SELECT product_id, COUNT(*) AS n FROM order_lines GROUP BY product_id)
-- END SOLUTION
"""
U.check("l12_lines_per_product", SQL_6)

# %% [markdown]
# ## 4 · The annotated schema · 9 min
#
# ✏️ **Exercise 7** · Complete the two tables. For each table: its key (columns separated by
# commas) and its grain. For each relationship: the fewest and the most rows on the many side
# for one row on the one side, written `fewest..most`, from your counts above.

# %%
SCHEMA = """
table       | key                  | one row per
-- BEGIN SOLUTION
stores      | store_id             | dispatch store
products    | product_id           | product in the catalogue
customers   | customer_id          | registered customer
orders      | order_id             | order placed by a customer at one store
order_lines | order_id, line_no    | line of one order: one product, a quantity and a price
deliveries  | delivery_id          | attempt to deliver one order
-- END SOLUTION

relationship              | fewest..most
-- BEGIN SOLUTION
customers->orders         | 0..52
orders->order_lines       | 1..7
orders->deliveries        | 0..3
products->order_lines     | 0..4525
-- END SOLUTION
"""
U.check_schema(SCHEMA)

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why is the fewest number of attempts per order 0 and not 1?</summary>
#
# Cancelled orders were never dispatched: they have no row in `deliveries`. Grouping `deliveries`
# alone cannot show them; only counting from `orders` can.
# </details>
#
# <details><summary>2. A colleague joins orders to deliveries and sums delivery fees. What goes wrong?</summary>
#
# Each order appears once per attempt, so an order delivered on the second attempt pays its fee
# twice. The grain of the join is the attempt, not the order.
# </details>
#
# <details><summary>3. Which key would you give deliveries if delivery_id did not exist?</summary>
#
# The pair `(order_id, attempt_no)`: the schema already declares it UNIQUE.
# </details>
#
# **Carry forward**: the annotated schema is assessed. Keep this notebook; Day 3 returns to the
# joins that multiply rows.
