# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 1.3 · One wide table, and what it repeats
#
# Day 1 · Session 3 (Normal forms, wide tables and embedded engines) · 30 min.
#
# Analysts like one wide table: every line with its store, region and category beside it. You
# build one, count what it repeats, make one copy of a fact disagree with another, and then run
# the same small query in a second embedded engine.
#
# AI policy for this lab: an assistant may explain an error message to you; it does not write
# your queries.
#
# **Tasks**
# - [ ] Build a wide table of order lines with store and product columns · 8 min
# - [ ] Count how often each store's region is repeated · 6 min
# - [ ] Change one region in the wide table and find the rows that now disagree · 8 min
# - [ ] Run the same count in the second embedded engine · 8 min
# - [ ] ✱ Stretch · Write two sentences on when the wide table is the right choice and who must rebuild it

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
w = U.workspace()  # writable memory; the company's six tables readable by name

# %% [markdown]
# ## 1 · Build the wide table · 8 min
#
# ✏️ **Exercise 1** · Create a table `wide` with one row per order line and these columns:
# `order_id, line_no, product_id, category, store_id, store_region, quantity, unit_price`.
# Join `order_lines` to `orders` (for the store), `stores` (for its region) and `products`
# (for the category).

# %%
SQL_1 = """
-- BEGIN SOLUTION
CREATE TABLE wide AS
SELECT l.order_id, l.line_no, l.product_id, p.category,
       o.store_id, s.region AS store_region, l.quantity, l.unit_price
FROM order_lines l
JOIN orders o   ON o.order_id = l.order_id
JOIN stores s   ON s.store_id = o.store_id
JOIN products p ON p.product_id = l.product_id
-- END SOLUTION
"""
if not U._blank(SQL_1):
    w.execute(SQL_1)
else:  # safety net: build it for you so the next cells run
    w.execute("""CREATE TABLE wide AS SELECT l.order_id, l.line_no, l.product_id, p.category, o.store_id,
                 s.region AS store_region, l.quantity, l.unit_price FROM order_lines l
                 JOIN orders o ON o.order_id = l.order_id JOIN stores s ON s.store_id = o.store_id
                 JOIN products p ON p.product_id = l.product_id""")
    print("not written yet: the wide table was built for you")
U.check("l13_wide_rows", "SELECT COUNT(*) AS rows FROM wide", con=w)

# %% [markdown]
# The wide table has as many rows as `order_lines`: every join went from the many side to a one
# side, so nothing multiplied.
#
# ## 2 · What it repeats · 6 min
#
# In `stores`, each store's region is written once. In `wide` it is written once per line.
#
# ✏️ **Exercise 2** · For each store, how many rows of `wide` carry its region? Return
# `store_id, copies`, by `store_id`.

# %%
SQL_2 = """
-- BEGIN SOLUTION
SELECT store_id, COUNT(store_region) AS copies
FROM wide
GROUP BY store_id
ORDER BY store_id
-- END SOLUTION
"""
U.check("l13_copies", SQL_2, con=w)

# %% [markdown]
# ## 3 · Make one copy disagree · 8 min
#
# Suppose store S06 is reassigned from Central to East, and someone fixes the wide table only
# for the lines of the first thousand orders. Run the cell: it makes that partial change.

# %%
w.execute("UPDATE wide SET store_region = 'East' WHERE store_id = 'S06' AND order_id < 'O0001000'")
print("partial update done")

# %% [markdown]
# ✏️ **Exercise 3** · Find every store that now has more than one region in `wide`, with the
# number of different regions. Return `store_id, regions`.

# %%
SQL_3 = """
-- BEGIN SOLUTION
SELECT store_id, COUNT(DISTINCT store_region) AS regions
FROM wide
GROUP BY store_id
HAVING COUNT(DISTINCT store_region) > 1
-- END SOLUTION
"""
U.check("l13_disagree", SQL_3, con=w)

# %% [markdown]
# **Look at** the result. The schema cannot disagree with itself here: the region lives in one
# row of `stores`. The wide table can. This is the update anomaly that normal forms remove.
#
# ## 4 · The same query in a second embedded engine · 8 min
#
# Both engines of this course are embedded: a library inside your Python process that reads a
# file, with no server to connect to. SQLite comes with Python's standard library. The cell below
# loads the mini tables into SQLite.

# %%
lite = U.mini_sqlite()
U.show("SELECT * FROM stores", lite)

# %% [markdown]
# ✏️ **Exercise 4** · On the mini tables, count order lines per store region. Return
# `region, lines`, by `region`. The same query runs in both engines below.

# %%
SQL_4 = """
-- BEGIN SOLUTION
SELECT s.region, COUNT(*) AS lines
FROM order_lines l
JOIN orders o ON o.order_id = l.order_id
JOIN stores s ON s.store_id = o.store_id
GROUP BY s.region
ORDER BY s.region
-- END SOLUTION
"""
print("SQLite:")
U.check("l13_two_engines", SQL_4, con=lite)
print("DuckDB:")
U.check("l13_two_engines", SQL_4, con=U.mini())

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why did the wide table not have more rows than order_lines?</summary>
#
# Each join went from a line to its one order, one store and one product. Only a join towards a
# many side, such as deliveries, multiplies rows.
# </details>
#
# <details><summary>2. Where should the region of a store be corrected, and why?</summary>
#
# In `stores`, once. Then the wide table is rebuilt from the schema. Fixing copies leaves some
# rows behind, as exercise 3 showed.
# </details>
#
# <details><summary>3. What would change if the data lived in a client-server database?</summary>
#
# The SQL would be almost the same. You would connect to a server over the network with an
# account, many people could write at once, and the server would manage access.
# </details>
#
# **Carry forward**: nothing; lab 1.4 starts from the company's database.
