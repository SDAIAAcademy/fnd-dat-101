# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 4.1 · Load the extracts and log every rejected row
#
# Day 4 · Session 1 (Loading into constrained tables, and transactions) · 35 min.
#
# The July extracts of customers, orders and order lines arrived from the order system as three
# CSV files (`data/extracts/`). They have defects: repeated keys, missing keys, values outside
# the allowed lists, impossible dates, lines of orders that do not exist. You define the three
# tables so that the database itself refuses such rows, stage the files as text, give every bad
# row a reason, load the rest in one transaction and write a load log in which every file reads
# as loaded plus rejected.
#
# AI policy: an assistant may explain an error message to you; it does not write the
# definitions or the rules. If you paste an error, paste the message and the column names, never
# rows of the files.
#
# **Tasks**
# - [ ] Write the three table definitions with their keys and checks · 10 min
# - [ ] Load the three extracts into all-text staging tables · 4 min
# - [ ] Write the reject rules for orders and order lines, each with a reason · 10 min
# - [ ] Insert the valid rows inside a transaction and write the load log · 8 min
# - [ ] Check that read equals loaded plus rejected for every file · 3 min
# - [ ] ✱ Stretch · Correct one rejected order with an UPDATE inside a transaction, roll it back and confirm nothing changed

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

# %% [markdown]
# ## 1 · Three definitions · 10 min
#
# The rules the order system promises, and that the database should enforce:
#
# | Table | Columns, in this order | Rules |
# |---|---|---|
# | customers | customer_id, joined_on (date), region, full_name, phone, email, birth_year (integer), marketing_opt_in (boolean) | the key is present and unique; region is one of North, South, East, West, Central |
# | orders | order_id, customer_id, store_id, ordered_at (timestamp), status, delivery_fee (decimal 10,2) | the key is unique; the customer exists in customers; status is delivered, returned or cancelled |
# | order_lines | order_id, line_no (integer), product_id, quantity (integer), unit_price (decimal 10,2), discount (decimal 10,2, may be empty), line_status | one row per order and line number; the order exists in orders; quantity is above 0 |
#
# ✏️ **Exercise 1** · Write the three `CREATE TABLE` statements. The checker runs them in an
# empty database and tries eleven rows against them, good and bad: a good row must go in, a bad
# one must be refused. It saves your script as `answers/july_schema.sql`.

# %%
DDL = """
-- BEGIN SOLUTION
CREATE TABLE customers (
  customer_id      VARCHAR PRIMARY KEY,
  joined_on        DATE NOT NULL,
  region           VARCHAR NOT NULL CHECK (region IN ('North', 'South', 'East', 'West', 'Central')),
  full_name        VARCHAR,
  phone            VARCHAR,
  email            VARCHAR,
  birth_year       INTEGER,
  marketing_opt_in BOOLEAN
);
CREATE TABLE orders (
  order_id     VARCHAR PRIMARY KEY,
  customer_id  VARCHAR NOT NULL REFERENCES customers (customer_id),
  store_id     VARCHAR NOT NULL,
  ordered_at   TIMESTAMP NOT NULL,
  status       VARCHAR NOT NULL CHECK (status IN ('delivered', 'returned', 'cancelled')),
  delivery_fee DECIMAL(10,2) NOT NULL
);
CREATE TABLE order_lines (
  order_id    VARCHAR NOT NULL REFERENCES orders (order_id),
  line_no     INTEGER NOT NULL,
  product_id  VARCHAR NOT NULL,
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  unit_price  DECIMAL(10,2) NOT NULL,
  discount    DECIMAL(10,2),
  line_status VARCHAR NOT NULL,
  PRIMARY KEY (order_id, line_no)
);
-- END SOLUTION
"""
U.check_definitions(DDL)

# %% [markdown]
# **Look at** which probe a missing `NOT NULL` lets through. A primary key refuses an empty key
# by itself; a plain column does not.
#
# ## 2 · Stage the files as text · 4 min
#
# Loading a raw file straight into a constrained table stops at the first bad row, and you learn
# about one defect at a time. Staging tables hold every row as text, numbered in file order, so
# you can look at all of them first. Run the cell: it creates your tables in a fresh database and
# stages the extracts as `stg_customers`, `stg_orders` and `stg_order_lines`.

# %%
con = U.july_workspace(DDL)
U.show("SELECT * FROM stg_orders", con, n=5)

# %% [markdown]
# ## 3 · Reject rules · 10 min
#
# A reject rule is a query over a staging table that returns each row's number, its key and a
# **reason**: empty for a good row, otherwise the first rule the row breaks. The helper keeps the
# rows with a reason as `rej_<table>` and the others as the view `ok_<table>`.
#
# Worked example, for customers. Read the order of the `WHEN` lines: a row is given one reason
# only, the first that applies, so the counts in the log add up.

# %%
REJ_CUSTOMERS = """
SELECT row_no, customer_id,
       CASE
         WHEN customer_id IS NULL OR TRIM(customer_id) = '' THEN 'missing key'
         WHEN ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY row_no) > 1 THEN 'duplicate key'
         WHEN region IS NULL OR region NOT IN ('North', 'South', 'East', 'West', 'Central') THEN 'unknown region'
         WHEN TRY_CAST(joined_on AS DATE) IS NULL THEN 'invalid date'
       END AS reason
FROM stg_customers
"""
U.rejects(con, "customers", REJ_CUSTOMERS)

# %% [markdown]
# ✏️ **Exercise 2** · The rule for orders, with these reasons in this order: `duplicate key`
# (a later row with an order number already seen), `unknown customer` (no row in
# `ok_customers` with that customer), `invalid status`, `invalid timestamp` (not of the form
# `2026-07-15 10:00:00`: `TRY_STRPTIME(ordered_at, '%Y-%m-%d %H:%M:%S')` returns NULL for those).

# %%
REJ_ORDERS = """
-- BEGIN SOLUTION
SELECT row_no, order_id,
       CASE
         WHEN ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY row_no) > 1 THEN 'duplicate key'
         WHEN NOT EXISTS (SELECT 1 FROM ok_customers c WHERE c.customer_id = s.customer_id) THEN 'unknown customer'
         WHEN status NOT IN ('delivered', 'returned', 'cancelled') THEN 'invalid status'
         WHEN TRY_STRPTIME(ordered_at, '%Y-%m-%d %H:%M:%S') IS NULL THEN 'invalid timestamp'
       END AS reason
FROM stg_orders s
-- END SOLUTION
"""
U.rejects(con, "orders", REJ_ORDERS)

# %% [markdown]
# ✏️ **Exercise 3** · The rule for order lines: `duplicate key` (the same order and line number
# again), `unknown order` (no row in `ok_orders` with that order: this includes the lines of
# orders you just rejected), `invalid price` (a price that does not read as a number),
# `invalid quantity` (not a whole number above 0).

# %%
REJ_LINES = """
-- BEGIN SOLUTION
SELECT row_no, order_id, line_no,
       CASE
         WHEN ROW_NUMBER() OVER (PARTITION BY order_id, line_no ORDER BY row_no) > 1 THEN 'duplicate key'
         WHEN NOT EXISTS (SELECT 1 FROM ok_orders o WHERE o.order_id = s.order_id) THEN 'unknown order'
         WHEN TRY_CAST(unit_price AS DECIMAL(10,2)) IS NULL THEN 'invalid price'
         WHEN TRY_CAST(quantity AS INTEGER) IS NULL OR TRY_CAST(quantity AS INTEGER) <= 0 THEN 'invalid quantity'
       END AS reason
FROM stg_order_lines s
-- END SOLUTION
"""
U.rejects(con, "order_lines", REJ_LINES)

# %% [markdown]
# ## 4 · One transaction, then the log · 8 min
#
# The three inserts go in together or not at all: a half-loaded month, with orders but without
# their lines, is worse than none. The helper runs your statements between `BEGIN` and `COMMIT`,
# and rolls everything back if one fails. The customers insert is written for you.
#
# ✏️ **Exercise 4** · Add the inserts of orders and order lines from `ok_orders` and
# `ok_order_lines`, converting each text column to the type of its table.

# %%
INSERTS = """
INSERT INTO customers
SELECT customer_id, CAST(joined_on AS DATE), region, full_name, phone, email,
       CAST(birth_year AS INTEGER), CAST(marketing_opt_in AS BOOLEAN)
FROM ok_customers;
-- BEGIN SOLUTION
INSERT INTO orders
SELECT order_id, customer_id, store_id, CAST(ordered_at AS TIMESTAMP), status,
       CAST(delivery_fee AS DECIMAL(10,2))
FROM ok_orders;
INSERT INTO order_lines
SELECT order_id, CAST(line_no AS INTEGER), product_id, CAST(quantity AS INTEGER),
       CAST(unit_price AS DECIMAL(10,2)), CAST(discount AS DECIMAL(10,2)), line_status
FROM ok_order_lines;
-- END SOLUTION
"""
U.in_transaction(con, INSERTS)

# %% [markdown]
# ## 5 · Read equals loaded plus rejected · 3 min
#
# The log counts every file three ways and compares the result with the log the trainer
# expects. It is saved as `answers/load_log.csv`: lab 4.2 starts from this load.

# %%
log = U.load_log(con)

# %% [markdown]
# **Look at** the unknown orders. Only some of them were missing from the file: the others are
# the lines of orders you rejected. A rule upstream changes counts downstream, and the log
# shows it.
#
# ## ✱ Stretch · Change and undo · optional
#
# One order was rejected for the status `deliverd`. Inside a transaction, correct a copy of it
# in the staging table, look at the row, then roll back and confirm the staging row is as it was.

# %%
STRETCH = """
-- BEGIN SOLUTION
BEGIN TRANSACTION;
UPDATE stg_orders SET status = 'delivered' WHERE status = 'deliverd' AND row_no = (SELECT MIN(row_no) FROM stg_orders WHERE status = 'deliverd');
SELECT COUNT(*) AS still_misspelt FROM stg_orders WHERE status = 'deliverd';
-- END SOLUTION
"""
if not U._blank(STRETCH):
    U.show(STRETCH, con)
    con.execute("ROLLBACK")
    U.show("SELECT COUNT(*) AS misspelt_after_rollback FROM stg_orders WHERE status = 'deliverd'", con)

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why stage as text instead of loading the file into the table?</summary>
#
# A constrained table refuses the whole insert at the first bad row. As text, every row is in,
# so you can give each bad row a reason and count them before anything reaches the real table.
# </details>
#
# <details><summary>2. Why does the order of the WHEN lines matter?</summary>
#
# A CASE returns the first branch that is true. One row gets one reason, so the rejected rows add
# up to the number rejected, and a duplicate that also has a bad region counts once.
# </details>
#
# <details><summary>3. What would happen without the transaction if the lines insert failed?</summary>
#
# The customers and orders would stay loaded without their lines. Reports of July would count
# orders with no revenue until someone noticed.
# </details>
#
# <details><summary>4. Who should sign off the load log before July is reported?</summary>
#
# Someone other than the person who wrote the reject rules: segregation of duties. The owner of
# the data, for example the finance controller for orders, reads the log and the rejected rows
# and accepts the load; the loader does not approve their own work.
# </details>
#
# **Carry forward**: `answers/july_schema.sql` and `answers/load_log.csv`. Lab 4.2 opens the July
# tables as a correct load leaves them.
