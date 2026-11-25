# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 4.3 · Read two plans and watch an index change one
#
# Day 4 · Session 3 (Query plans and indexes) · 30 min.
#
# `EXPLAIN` shows how an engine intends to run a query, before it runs it. You read the plan of
# a join with a filter in DuckDB, then load the orders into SQLite (Python's standard library)
# and watch an index turn a scan of every row into a search. This lab reads plan shapes only:
# timings on a laptop vary too much to teach from, so none are taken.
#
# AI policy: an assistant may explain an operator's name or an error message; you read the
# plan yourself.
#
# **Tasks**
# - [ ] Read the plan of a join and group query · 8 min
# - [ ] Find where the filter is applied · 5 min
# - [ ] Read the plan of a lookup in the second engine before an index · 5 min
# - [ ] Create the index and read the new plan · 6 min
# - [ ] Write when an index helps an analytical query and when it does not · 6 min
# - [ ] ✱ Stretch · Create a two-column index and find which order of the columns the lookup can use

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
# ## 1 · A plan in DuckDB · 8 min
#
# The query: gross line value of delivered orders, by store. Put `EXPLAIN` in front of it and
# run it. Read the plan **from the bottom up**: the boxes at the bottom read the tables, each box
# above takes the rows from the box below it.
#
# ```sql
# SELECT o.store_id, SUM(l.quantity * l.unit_price) AS gross
# FROM orders o
# JOIN order_lines l ON l.order_id = o.order_id
# WHERE o.status = 'delivered'
# GROUP BY o.store_id
# ```
#
# ✏️ **Exercise 1** · Write the `EXPLAIN` statement.

# %%
PLAN_1 = """
-- BEGIN SOLUTION
EXPLAIN
SELECT o.store_id, SUM(l.quantity * l.unit_price) AS gross
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY o.store_id
-- END SOLUTION
"""
plan_1 = U.plan_duckdb(PLAN_1, con)

# %% [markdown]
# The numbers after `~` are the engine's **estimates** of the rows, made before running: they
# are not counts.
#
# ## 2 · Where the filter is · 5 min
#
# ✏️ **Exercise 2** · Answer from the plan, one word or two after each bar: the operator at the
# bottom, the operator that joins, the operator that groups, the table whose scan carries the
# filter, and whether the filter is applied `before` or `after` the join.

# %%
READING = """
-- BEGIN SOLUTION
bottom_operator    | seq scan
join_operator      | hash join
group_operator     | hash group by
filter_table       | orders
filter_vs_join     | before
-- END SOLUTION
"""
U.check_pairs("l43_reading", READING)

# %% [markdown]
# **Look at** the estimate above the filtered scan: about a third of the orders. The engine
# drops the other orders while reading them, so the join has fewer rows to match.
#
# ## 3 · A lookup in SQLite, before an index · 5 min
#
# The cell loads the 250,000 orders into SQLite, in memory, with no index (a few seconds).
# In SQLite the statement is `EXPLAIN QUERY PLAN`, and the lines read `SCAN` (every row) or
# `SEARCH` (straight to the matching rows).
#
# ✏️ **Exercise 3** · The plan of: every order of customer `C00042`.

# %%
lite = U.sqlite_orders()
PLAN_2 = """
-- BEGIN SOLUTION
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 'C00042'
-- END SOLUTION
"""
plan_2 = U.plan_sqlite(lite, PLAN_2)
U.expect_plan(plan_2, "SCAN", "before the index")

# %% [markdown]
# ## 4 · The index · 6 min
#
# ✏️ **Exercise 4** · Create an index named `ix_orders_customer` on the customer column, then
# read the plan of the same lookup again.

# %%
INDEX = """
-- BEGIN SOLUTION
CREATE INDEX ix_orders_customer ON orders (customer_id)
-- END SOLUTION
"""
if not U._blank(INDEX):
    lite.execute(INDEX)
plan_3 = U.plan_sqlite(lite, PLAN_2)
U.expect_plan(plan_3, "SEARCH", "after the index")

# %% [markdown]
# ## 5 · When an index helps · 6 min
#
# ✏️ **Exercise 5** · With the index in place, predict `scan` or `search` for each query, then
# run the cell to see the plans.
#
# | Key | Query |
# |---|---|
# | k1 | `SELECT * FROM orders WHERE customer_id = 'C01000'` |
# | k2 | `SELECT status, COUNT(*) FROM orders GROUP BY status` |
# | k3 | `SELECT COUNT(*) FROM orders WHERE customer_id LIKE '%42'` |
# | k4 | `SELECT * FROM orders WHERE store_id = 'S03'` |

# %%
PREDICT = """
-- BEGIN SOLUTION
k1 | search
k2 | scan
k3 | scan
k4 | scan
-- END SOLUTION
"""
U.check_pairs("l43_predict", PREDICT)
for key, q in [("k1", "SELECT * FROM orders WHERE customer_id = 'C01000'"),
               ("k2", "SELECT status, COUNT(*) FROM orders GROUP BY status"),
               ("k3", "SELECT COUNT(*) FROM orders WHERE customer_id LIKE '%42'"),
               ("k4", "SELECT * FROM orders WHERE store_id = 'S03'")]:
    print(key, end=": ")
    U.plan_sqlite(lite, "EXPLAIN QUERY PLAN " + q)

# %% [markdown]
# **Look at** k3: SQLite reads the whole index instead of the table (`COVERING INDEX`), but it
# still reads every entry. A pattern that starts with `%` cannot jump to a place in the index.
#
# ✏️ In two sentences: when does an index help, and why does an analytical query that reads
# most of a table rarely gain from one?

# %%
RULE = """
-- BEGIN SOLUTION
An index helps when a query picks a few rows by an exact value or a range of the indexed column,
because the engine can go straight to them. A query that reads most of the table, such as a
total by store over the year, has to read every row anyway, so the index has nothing to skip.
-- END SOLUTION
"""
print(RULE)

# %% [markdown]
# ## ✱ Stretch · Two columns, in an order · optional
#
# Create an index on `(store_id, ordered_at)`. Which of these two lookups can search it:
# orders since 1 March 2026 of every store, or orders since 1 March 2026 of store `S01`?

# %%
STRETCH = """
-- BEGIN SOLUTION
CREATE INDEX ix_orders_store_time ON orders (store_id, ordered_at)
-- END SOLUTION
"""
if not U._blank(STRETCH):
    lite.execute(STRETCH)
    U.plan_sqlite(lite, "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE ordered_at >= '2026-03-01'")
    U.plan_sqlite(lite, "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE store_id = 'S01' AND ordered_at >= '2026-03-01'")

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why read a plan from the bottom?</summary>
#
# The bottom operators read the tables; every operator above works on the rows that come up
# from below. The top box is the last step, the one that returns the result.
# </details>
#
# <details><summary>2. DuckDB showed a sequential scan with the filter inside it. Is that slow?</summary>
#
# Not for this question. It must look at every order to find the delivered ones, and DuckDB
# reads only the columns the query names, in large blocks. An index would not reduce the work.
# </details>
#
# <details><summary>3. Why are there no timings in this lab?</summary>
#
# The same query on the same laptop can take twice as long when something else runs. The plan's
# shape (scan or search, which join) is stable; it is what you can reason about and compare.
# </details>
#
# **Carry forward**: nothing; lab 4.4 uses the mini tables.
