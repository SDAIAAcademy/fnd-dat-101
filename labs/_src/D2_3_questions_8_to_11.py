# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 2.3 · Questions 8 to 11: groups
#
# Day 2 · Session 3 (Grouping and having) · 35 min.
#
# Four grouping questions. Before each one, say the grain of the result: one row per what?
# Predict, then query. The answers go to `answers/part3.sql`.
#
# AI policy: the predictions are written with the assistant off. In the queries, an assistant
# may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Write a prediction for each of the four questions · 5 min
# - [ ] Question 8: delivered orders per store · 7 min
# - [ ] Question 9: customers with many orders, using HAVING · 8 min
# - [ ] Question 10: orders and distinct customers per month · 7 min
# - [ ] Question 11: products on many order lines · 5 min
# - [ ] Save the part file · 3 min
# - [ ] ✱ Stretch · Explain why COUNT(discount) and COUNT(*) differ on the order lines

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
PRED_Q08 = """
-- BEGIN SOLUTION
eight rows, one per store; S08 the smallest, it opened in April
-- END SOLUTION
"""
PRED_Q09 = """
-- BEGIN SOLUTION
a short list, under twenty customers
-- END SOLUTION
"""
PRED_Q10 = """
-- BEGIN SOLUTION
six rows, January to June; distinct customers far fewer than orders
-- END SOLUTION
"""
PRED_Q11 = """
-- BEGIN SOLUTION
about a dozen products
-- END SOLUTION
"""

# %% [markdown]
# ## 2 · Four groups · 27 min

# %% [markdown]
# **Question 8.** How many delivered orders did each store dispatch? Columns `store_id, orders`, by `store_id`.

# %%
SQL_Q08 = """
-- BEGIN SOLUTION
SELECT store_id, COUNT(*) AS orders
FROM orders
WHERE status = 'delivered'
GROUP BY store_id
ORDER BY store_id
-- END SOLUTION
"""
U.check("q08", SQL_Q08)

# %% [markdown]
# **Question 9.** Which customers placed at least 48 orders of any status? Columns `customer_id, orders`, by
# orders from the most, then `customer_id`. The condition is on a count: it belongs in `HAVING`.

# %%
SQL_Q09 = """
-- BEGIN SOLUTION
SELECT customer_id, COUNT(*) AS orders
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 48
ORDER BY orders DESC, customer_id
-- END SOLUTION
"""
U.check("q09", SQL_Q09)

# %% [markdown]
# **Question 10.** For each month, by the date the order was placed: how many orders, and how many different
# customers? Columns `month, orders, customers`, the month as its first day, by `month`.
# `date_trunc('month', ordered_at)` gives the first instant of the month; cast it to `DATE`.

# %%
SQL_Q10 = """
-- BEGIN SOLUTION
SELECT CAST(date_trunc('month', ordered_at) AS DATE) AS month,
       COUNT(*) AS orders,
       COUNT(DISTINCT customer_id) AS customers
FROM orders
GROUP BY month
ORDER BY month
-- END SOLUTION
"""
U.check("q10", SQL_Q10)

# %% [markdown]
# **Question 11.** Which products appear on at least 4,000 order lines? Columns `product_id, lines`, by lines
# from the most, then `product_id`.

# %%
SQL_Q11 = """
-- BEGIN SOLUTION
SELECT product_id, COUNT(*) AS lines
FROM order_lines
GROUP BY product_id
HAVING COUNT(*) >= 4000
ORDER BY lines DESC, product_id
-- END SOLUTION
"""
U.check("q11", SQL_Q11)

# %% [markdown]
# **Look at** COUNT(*) against COUNT(discount) on the order lines: one counts rows, the other
# counts values that are not NULL.

# %%
U.show("SELECT COUNT(*) AS rows, COUNT(discount) AS discounts_recorded FROM order_lines")

# %% [markdown]
# ## 3 · Save the part file · 3 min

# %%
U.save_part("part3", {"q08": (PRED_Q08, SQL_Q08), "q09": (PRED_Q09, SQL_Q09), "q10": (PRED_Q10, SQL_Q10), "q11": (PRED_Q11, SQL_Q11)})

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why can question 9 not put `COUNT(*) >= 48` in WHERE?</summary>
#
# WHERE filters rows before the groups exist; a count only exists after grouping. HAVING filters groups.
# </details>
#
# <details><summary>2. How many rows does question 10 return, and why?</summary>
#
# Six: one per month of placing, because the data covers January to June.
# </details>
#
# <details><summary>3. What is the grain of the result of question 8?</summary>
#
# One row per store, holding the number of its delivered orders.
# </details>
#
# **Carry forward**: `answers/part3.sql`, read by the checker in lab 3.2.
