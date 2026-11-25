# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Pre-work · Ten first queries on the mini tables
#
# Before Day 1 · guided self-study · about 2 hours, after `00_setup_check.ipynb`.
#
# Six tiny tables of the grocery delivery company, small enough to read on one screen. You
# read them, then write ten short queries, each checked as you run it. Coming from
# spreadsheets: a table is a sheet with fixed columns, `WHERE` is a filter, `ORDER BY` a sort,
# and a computed column is a formula written once for every row.
#
# AI policy: AI-off. These drills build the reflexes the course relies on; an assistant that
# writes them for you takes that away.
#
# **Tasks**
# - [ ] Read the six mini tables and say what one row of each stands for · 20 min
# - [ ] Write drills 1 to 5: columns, filters and sorting · 40 min
# - [ ] Write drills 6 to 10: computed columns, counts and ranges · 45 min
# - [ ] Answer the three questions at the end · 15 min

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
m = U.mini()

# %% [markdown]
# ## 1 · Read the tables · 20 min
#
# For each table, say in one sentence what one row stands for. Day 1 calls this the grain.

# %%
for t in ["stores", "products", "customers", "orders", "order_lines", "deliveries"]:
    print(f"\n{t}")
    U.show(f"SELECT * FROM {t}", m, n=20)

# %% [markdown]
# ## 2 · Columns, filters and sorting · 40 min
#
# ✏️ **Drill 1** · Every product: `product_id`, `product_name` and `list_price`.

# %%
SQL_1 = """
-- BEGIN SOLUTION
SELECT product_id, product_name, list_price
FROM products
-- END SOLUTION
"""
U.check("p01", SQL_1, con=m)

# %% [markdown]
# ✏️ **Drill 2** · The orders of store `S01`: `order_id` and `ordered_at`.

# %%
SQL_2 = """
-- BEGIN SOLUTION
SELECT order_id, ordered_at
FROM orders
WHERE store_id = 'S01'
-- END SOLUTION
"""
U.check("p02", SQL_2, con=m)

# %% [markdown]
# ✏️ **Drill 3** · The three most recent orders, newest first: `order_id`, `ordered_at`.

# %%
SQL_3 = """
-- BEGIN SOLUTION
SELECT order_id, ordered_at
FROM orders
ORDER BY ordered_at DESC
LIMIT 3
-- END SOLUTION
"""
U.check("p03", SQL_3, con=m)

# %% [markdown]
# ✏️ **Drill 4** · Order lines with a quantity of 2 or more: `order_id`, `line_no`, `quantity`.

# %%
SQL_4 = """
-- BEGIN SOLUTION
SELECT order_id, line_no, quantity
FROM order_lines
WHERE quantity >= 2
-- END SOLUTION
"""
U.check("p04", SQL_4, con=m)

# %% [markdown]
# ✏️ **Drill 5** · Orders with the status `delivered` placed at store `S02`: `order_id`.

# %%
SQL_5 = """
-- BEGIN SOLUTION
SELECT order_id
FROM orders
WHERE status = 'delivered' AND store_id = 'S02'
-- END SOLUTION
"""
U.check("p05", SQL_5, con=m)

# %% [markdown]
# ## 3 · Computed columns, counts and ranges · 45 min
#
# ✏️ **Drill 6** · The lines of order `O01` with their value, quantity times unit price:
# `line_no`, `line_value`.

# %%
SQL_6 = """
-- BEGIN SOLUTION
SELECT line_no, quantity * unit_price AS line_value
FROM order_lines
WHERE order_id = 'O01'
-- END SOLUTION
"""
U.check("p06", SQL_6, con=m)

# %% [markdown]
# ✏️ **Drill 7** · How many orders are there? One column, `orders`.

# %%
SQL_7 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS orders
FROM orders
-- END SOLUTION
"""
U.check("p07", SQL_7, con=m)

# %% [markdown]
# ✏️ **Drill 8** · Products with a list price from 5 to 10 riyals, both included:
# `product_id`, `list_price`.

# %%
SQL_8 = """
-- BEGIN SOLUTION
SELECT product_id, list_price
FROM products
WHERE list_price >= 5 AND list_price <= 10
-- END SOLUTION
"""
U.check("p08", SQL_8, con=m)

# %% [markdown]
# ✏️ **Drill 9** · Delivery attempts made on 2 March 2026, any time of day: `delivery_id`.
# A timestamp is a date and a time: compare with the start of the day and the start of the next.

# %%
SQL_9 = """
-- BEGIN SOLUTION
SELECT delivery_id
FROM deliveries
WHERE attempted_at >= TIMESTAMP '2026-03-02 00:00:00'
  AND attempted_at <  TIMESTAMP '2026-03-03 00:00:00'
-- END SOLUTION
"""
U.check("p09", SQL_9, con=m)

# %% [markdown]
# ✏️ **Drill 10** · The largest and the smallest unit price on any order line: `highest`,
# `lowest`.

# %%
SQL_10 = """
-- BEGIN SOLUTION
SELECT MAX(unit_price) AS highest, MIN(unit_price) AS lowest
FROM order_lines
-- END SOLUTION
"""
U.check("p10", SQL_10, con=m)

# %% [markdown]
# ## Check yourself · 15 min
#
# <details><summary>1. What does one row of order_lines stand for?</summary>
#
# One product on one order: an order with three products has three lines.
# </details>
#
# <details><summary>2. Why compare drill 9 with the start of the next day instead of "= '2026-03-02'"?</summary>
#
# The column holds a time as well. Equal to the date would match only midnight; the range keeps
# every time of that day.
# </details>
#
# <details><summary>3. Drill 7 counted the orders. Would counting the order lines give the same number?</summary>
#
# No: an order has one or more lines, so there are more lines than orders. Day 1 starts from
# this difference.
# </details>
#
# **Carry forward**: nothing; Day 1 opens the full database.
