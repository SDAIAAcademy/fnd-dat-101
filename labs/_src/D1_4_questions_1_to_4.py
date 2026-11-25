# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 1.4 · Questions 1 to 4, predicted first
#
# Day 1 · Session 4 (Filters, sorting and expressions) · 35 min.
#
# The head of commercial reporting sent twenty questions (`data/twenty_questions.md`). Today you
# answer the first four. For each one, write your prediction first, then the query; compare the
# two. The answers are saved to `answers/part1.sql`; the automatic checker of lab 3.2 reads all
# your part files.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Read the four questions and write a prediction for each · 5 min
# - [ ] Answer questions 1 and 2: a text filter and a date range · 12 min
# - [ ] Answer questions 3 and 4: a sorted top ten and a line value · 12 min
# - [ ] Compare each result with your prediction and save the part file · 6 min
# - [ ] ✱ Stretch · Rewrite question 2 with a half-open date range and explain why it is safer than BETWEEN

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
# ✏️ Write one line per question: how many rows, or roughly what value, or what the first row
# will be. Keep it honest: a wrong prediction you then understand is worth more than a right guess.

# %%
PRED_Q01 = """
-- BEGIN SOLUTION
about twenty rows, all of them White cheese in different sizes
-- END SOLUTION
"""
PRED_Q02 = """
-- BEGIN SOLUTION
one number, about a sixth of 250,000 and a little more because March has 31 days: about 43,000
-- END SOLUTION
"""
PRED_Q03 = """
-- BEGIN SOLUTION
ten rows, mostly Pantry items, prices above 60
-- END SOLUTION
"""
PRED_Q04 = """
-- BEGIN SOLUTION
as many rows as the order has lines; lines with an empty discount keep their full value
-- END SOLUTION
"""

# %% [markdown]
# ## 2 · Questions 1 and 2 · 12 min
#
# **Question 1.** Which Dairy products have "cheese" in their name, in any letter case?
# Columns `product_id, product_name`, by `product_id`. `ILIKE` compares text without regard to
# letter case; `%` stands for any run of characters.

# %%
SQL_Q01 = """
-- BEGIN SOLUTION
SELECT product_id, product_name
FROM products
WHERE category = 'Dairy' AND product_name ILIKE '%cheese%'
ORDER BY product_id
-- END SOLUTION
"""
U.check("q01", SQL_Q01)

# %% [markdown]
# **Question 2.** How many orders, of any status, were placed in March 2026? One column,
# `orders`. `ordered_at` is a timestamp: a date and a time of day.

# %%
SQL_Q02 = """
-- BEGIN SOLUTION
SELECT COUNT(*) AS orders
FROM orders
WHERE ordered_at >= DATE '2026-03-01' AND ordered_at < DATE '2026-04-01'
-- END SOLUTION
"""
U.check("q02", SQL_Q02)

# %% [markdown]
# ## 3 · Questions 3 and 4 · 12 min
#
# **Question 3.** Which are the ten most expensive active products by list price? Columns
# `product_id, product_name, list_price`; by price from the highest, then `product_id`.

# %%
SQL_Q03 = """
-- BEGIN SOLUTION
SELECT product_id, product_name, list_price
FROM products
WHERE is_active
ORDER BY list_price DESC, product_id
LIMIT 10
-- END SOLUTION
"""
U.check("q03", SQL_Q03)

# %% [markdown]
# **Question 4.** The value of each line of order O0000018: quantity times unit price, minus the
# discount, where an empty discount means none. Columns `line_no, line_value`, by `line_no`.
# `COALESCE(x, 0)` gives `x`, or 0 when `x` is NULL.

# %%
SQL_Q04 = """
-- BEGIN SOLUTION
SELECT line_no, quantity * unit_price - COALESCE(discount, 0) AS line_value
FROM order_lines
WHERE order_id = 'O0000018'
ORDER BY line_no
-- END SOLUTION
"""
U.check("q04", SQL_Q04)

# %% [markdown]
# **Look at** what happens without `COALESCE`: run the cell. A line with an empty discount gets
# an empty value, and any sum over it would skip the line.

# %%
U.show("SELECT line_no, discount, quantity * unit_price - discount AS without_coalesce FROM order_lines WHERE order_id = 'O0000018' ORDER BY line_no")

# %% [markdown]
# ## 4 · Compare and save · 6 min
#
# Read each prediction beside its result. Then save the part file.

# %%
U.save_part("part1", {"q01": (PRED_Q01, SQL_Q01), "q02": (PRED_Q02, SQL_Q02),
                      "q03": (PRED_Q03, SQL_Q03), "q04": (PRED_Q04, SQL_Q04)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why is `ordered_at BETWEEN '2026-03-01' AND '2026-03-31'` wrong here?</summary>
#
# `'2026-03-31'` as a timestamp is the first instant of 31 March: every order placed later that
# day is left out. A half-open range, from the first of March up to but not including the first
# of April, keeps the whole last day.
# </details>
#
# <details><summary>2. Without the tie-breaker `product_id`, what could change in question 3?</summary>
#
# Products with the same price could come in a different order on another run, and the tenth row
# could be a different product.
# </details>
#
# <details><summary>3. What does `WHERE is_active` mean when the column is a boolean?</summary>
#
# Keep the rows where `is_active` is true. It is the same as `WHERE is_active = true`.
# </details>
#
# **Carry forward**: `answers/part1.sql`. If it is missing in lab 3.2, the checker counts these
# four questions as unanswered: run this notebook again to write it.
