# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 1.1 · Six tables and their keys
#
# Day 1 · Session 1 (Tables, types, keys and constraints) · 35 min.
#
# You open the grocery delivery company's database, read what each of its six tables holds,
# and test which columns really name a row. Then you try to put a bad row into a copy and read
# how the database refuses it. You write SQL in the cells marked ✏️; the rest is done for you.
#
# AI policy for this lab: an assistant may explain an error message to you; it does not write
# your queries.
#
# **Tasks**
# - [ ] List the six tables with their row counts · 5 min
# - [ ] Describe the columns and types of each table · 7 min
# - [ ] Test each candidate key: COUNT(*) against COUNT(DISTINCT key) · 10 min
# - [ ] Break a key and a check on the mini tables and read the refusals · 8 min
# - [ ] Write down what each table refuses and why · 5 min
# - [ ] ✱ Stretch · Find one column whose type is weaker than its meaning and say what that lets in

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
con = U.db()  # the first run writes the tables and builds the database: about 15 seconds

# %% [markdown]
# ## 1 · The six tables · 5 min
#
# The engine keeps a list of its own tables. Run the cell to see the six tables and their sizes.

# %%
U.show("SELECT table_name, estimated_size AS rows FROM duckdb_tables() ORDER BY table_name")

# %% [markdown]
# The list also shows `daily_orders`, a summary table built from the others for Day 3. The six
# tables of the schema are `stores`, `products`, `customers`, `orders`, `order_lines` and
# `deliveries`.
#
# ✏️ **Exercise 1** · Count the rows of `orders` exactly with `COUNT(*)`.

# %%
SQL_1 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS orders FROM orders
-- END SOLUTION
"""
U.check("l11_orders", SQL_1)

# %% [markdown]
# ## 2 · Columns and types · 7 min
#
# `DESCRIBE <table>` lists each column with its type, whether it may be NULL, and whether it is
# part of the primary key. Here is `customers`:

# %%
U.show("DESCRIBE customers")

# %% [markdown]
# ✏️ **Exercise 2** · Describe `order_lines`. Which two columns form its primary key? Which
# column may be NULL, and what would a NULL there mean?

# %%
SQL_2 = """
-- BEGIN SOLUTION
DESCRIBE order_lines
-- END SOLUTION
"""
U.check("l11_describe", SQL_2, ordered=True)

# %% [markdown]
# ## 3 · Test a candidate key by counting · 10 min
#
# A column (or a set of columns) is a key when no two rows share its value. Count the rows and
# count the distinct values: if the two numbers are equal, no value repeats.
#
# ✏️ **Exercise 3** · Is `order_id` alone a key of `order_lines`? Return two numbers:
# `n_rows` (all rows) and `n_orders` (distinct `order_id`).

# %%
SQL_3 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_id) AS n_orders
FROM order_lines
-- END SOLUTION
"""
U.check("l11_lines_key", SQL_3)

# %% [markdown]
# ✏️ **Exercise 4** · Now test the pair `(order_id, line_no)`: count the distinct pairs. Hint:
# select the distinct pairs in a subquery and count its rows.

# %%
SQL_4 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n_pairs
FROM (SELECT DISTINCT order_id, line_no FROM order_lines)
-- END SOLUTION
"""
U.check("l11_pair_key", SQL_4)

# %% [markdown]
# ✏️ **Exercise 5** · In `deliveries`, is `order_id` a key? Return `n_rows` and `n_orders`
# as in exercise 3. If it is not, a row of `deliveries` is not "one order": what is it?

# %%
SQL_5 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_id) AS n_orders
FROM deliveries
-- END SOLUTION
"""
U.check("l11_deliveries_key", SQL_5)

# %% [markdown]
# **Look at** the two pairs of numbers. In both tables the order appears more than once, for a
# different reason each time. Say the two reasons aloud before moving on.
#
# ## 4 · Break a key and a check · 8 min
#
# The mini tables are a tiny copy of the schema in memory, so you can change them freely.
# `orders` in the mini copy already holds an order `O01`.
#
# ✏️ **Exercise 6** · Write an `INSERT` into the mini `orders` that repeats the key `O01`.
# Columns, in order: `order_id, customer_id, store_id, ordered_at, status, delivery_fee`.

# %%
m = U.mini()
U.show("SELECT * FROM orders", m)

# %%
SQL_6 = """
-- BEGIN SOLUTION
INSERT INTO orders VALUES ('O01', 'C001', 'S01', TIMESTAMP '2026-03-09', 'delivered', 9.00)
-- END SOLUTION
"""
U.expect_refusal(m, SQL_6)

# %% [markdown]
# ✏️ **Exercise 7** · Write an `INSERT` into the mini `order_lines` with a quantity of 0 for
# order `O01`, line 3, product `P01`, price 6.50, no discount, status `ok`. Which rule refuses it?

# %%
SQL_7 = """
-- BEGIN SOLUTION
INSERT INTO order_lines VALUES ('O01', 3, 'P01', 0, 6.50, NULL, 'ok')
-- END SOLUTION
"""
U.expect_refusal(m, SQL_7)

# %% [markdown]
# ## 5 · What each table refuses · 5 min
#
# ✏️ **Exercise 8** · Complete the table in the cell below: one line per table, the rule that
# protects it most. You will reuse it in lab 1.2.

# %%
REFUSES = """
-- BEGIN SOLUTION
orders      | a second row with the same order_id; a status other than delivered, returned, cancelled; a customer or store that does not exist
order_lines | a second row with the same order_id and line_no; a quantity of 0 or less; an order or product that does not exist
deliveries  | a second attempt with the same order_id and attempt_no; an order that does not exist
customers   | a second row with the same customer_id; a region outside the five
products    | a second row with the same product_id; a price of 0 or less
stores      | a second row with the same store_id; a store without a region
-- END SOLUTION
"""
print(REFUSES)

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Exercise 3 gave two different numbers. What does that tell you?</summary>
#
# `order_id` repeats in `order_lines`: an order has several lines, so `order_id` alone is not a key.
# </details>
#
# <details><summary>2. Why did the insert of exercise 7 fail although every value had the right type?</summary>
#
# A type only says what kind of value fits; the CHECK constraint `quantity > 0` says which values
# make sense. Types and constraints are two different guards.
# </details>
#
# <details><summary>3. In `deliveries`, what does one row stand for?</summary>
#
# One delivery attempt. An order that failed once has two rows.
# </details>
#
# **Carry forward**: lab 1.2 starts from the same database; your table of refusals helps with the
# annotated schema.
