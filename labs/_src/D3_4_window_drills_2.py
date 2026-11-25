# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 3.4 · Window drills 2: weeks and seven days
#
# Day 3 · Session 4 (Running and moving aggregates) · 35 min.
#
# The daily order table `daily_orders` holds one row per store and order date with the orders
# and net sales of that day (by order date, as the operations dashboard counts them). You compute a
# week-on-week change, a running total within each month, and seven-day averages that stay right
# across days a store was closed. The drills are saved to `answers/windows2.sql`, then the window
# checker reads both window files.
#
# AI policy: an assistant may explain an error message to you; it does not write the query.
#
# **Tasks**
# - [ ] Drill 4: weekly orders per store and the change from the week before · 10 min
# - [ ] Drill 5: running net sales per store within each month · 8 min
# - [ ] Drill 6: seven-day average net sales, ROWS against RANGE · 10 min
# - [ ] Save the drills and run the window checker · 7 min
# - [ ] ✱ Stretch · Fill the closed days with zero rows from a calendar and compare the three seven-day averages

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

# %%
U.show("SELECT * FROM daily_orders WHERE store_id = 'S05' ORDER BY order_date LIMIT 5")

# %% [markdown]
# ## 1 · Drill 4: week-on-week change · 10 min
#
# Weekly orders per store (weeks start on Monday: `date_trunc('week', order_date)`), the
# previous week's orders, and the change. Columns `store_id, week, orders, previous_week, change`,
# by store, then week.

# %%
SQL_W4 = """
-- BEGIN SOLUTION
-- partition: one series per store, so each store is compared with its own previous week
WITH weekly AS (
  SELECT store_id, CAST(date_trunc('week', order_date) AS DATE) AS week, SUM(orders) AS orders
  FROM daily_orders
  GROUP BY store_id, week
)
SELECT store_id, week, orders,
       LAG(orders) OVER (PARTITION BY store_id ORDER BY week) AS previous_week,
       orders - LAG(orders) OVER (PARTITION BY store_id ORDER BY week) AS change
FROM weekly
ORDER BY store_id, week
-- END SOLUTION
"""
U.check("w4", SQL_W4)

# %% [markdown]
# **Look at** the first and last week of each store: 1 January 2026 was a Thursday, so the first
# week holds four days, and 30 June was a Tuesday. A change next to a partial week is not a trend.

# %% [markdown]
# ## 2 · Drill 5: month-to-date net sales · 8 min
#
# For store S05 in March 2026: each day's net sales and the running total since the first of
# the month. Columns `order_date, net_sales, month_to_date`, by date.

# %%
SQL_W5 = """
-- BEGIN SOLUTION
-- partition: one running total per month, restarting on the first day of each month
SELECT order_date, net_sales,
       SUM(net_sales) OVER (PARTITION BY date_trunc('month', order_date) ORDER BY order_date) AS month_to_date
FROM daily_orders
WHERE store_id = 'S05' AND order_date >= DATE '2026-03-01' AND order_date < DATE '2026-04-01'
ORDER BY order_date
-- END SOLUTION
"""
U.check("w5", SQL_W5)

# %% [markdown]
# ## 3 · Drill 6: seven-day averages, ROWS against RANGE · 10 min
#
# For store S05 from 8 to 20 March 2026: each day's net sales, the average of the last seven
# **rows** (`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`) and the average of the last seven
# **days** (`RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW`). Columns
# `order_date, net_sales, avg_7_rows, avg_7_days`, by date. Compute over all of March, then keep
# the dates asked for.

# %%
SQL_W6 = """
-- BEGIN SOLUTION
-- partition: none needed; one store is selected, ordered by date. The frame is what matters:
-- ROWS counts rows, RANGE counts days, and the store was closed for three days in March.
WITH march AS (
  SELECT order_date, net_sales,
         AVG(net_sales) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7_rows,
         AVG(net_sales) OVER (ORDER BY order_date RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW) AS avg_7_days
  FROM daily_orders
  WHERE store_id = 'S05' AND order_date >= DATE '2026-03-01' AND order_date < DATE '2026-04-01'
)
SELECT order_date, net_sales, ROUND(avg_7_rows, 2) AS avg_7_rows, ROUND(avg_7_days, 2) AS avg_7_days
FROM march
WHERE order_date BETWEEN DATE '2026-03-08' AND DATE '2026-03-20'
ORDER BY order_date
-- END SOLUTION
"""
U.check("w6", SQL_W6)

# %% [markdown]
# **Look at** the dates after the closed days: the ROWS frame reaches back more than seven
# calendar days, because the closed days have no rows. Neither frame counts a closed day as zero
# sales: the stretch does that with a calendar.

# %% [markdown]
# ## 4 · Save the drills and run the window checker · 7 min

# %%
U.save_part("windows2", {"w4": ("", SQL_W4), "w5": ("", SQL_W5), "w6": ("", SQL_W6)})
passed = U.grade_windows()

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why does drill 4 compute weekly totals before using LAG?</summary>
#
# LAG over daily rows would compare a day with the day before; the question compares weeks, so the grain must be the week first.
# </details>
#
# <details><summary>2. When do ROWS and RANGE frames give the same seven-day average?</summary>
#
# When every day has exactly one row: then seven rows are seven days.
# </details>
#
# <details><summary>3. What does month_to_date show on the first day of April, and why?</summary>
#
# Only that day's sales: the partition by month restarts the running total.
# </details>
#
# **Carry forward**: `answers/windows1.sql` and `answers/windows2.sql`: the assessed window file. If windows1 is missing, run lab 3.3 again.
