# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 4.2 · Label the tables and build the analyst view
#
# Day 4 · Session 2 (Views that limit what is exposed) · 35 min.
#
# The analysts of the grocery delivery company want to study July: how many customers joined in
# each region, how old the customer base is, and where revenue came from. They do not need to
# know who anyone is. You mark the personal-data columns of the customer table, label each table
# with a level under the company's rule, and build one view that answers the analysts' three
# questions without names, phones or e-mail addresses: the data protection officer agreed to the
# analysis on that condition.
#
# All names, phones and e-mail addresses here are synthetic and deliberately invalid
# (`Synthetic Person 40001`, `TEL-40001-X`, `c40001@example.invalid`). Treat them as if they were
# real: that is the exercise.
#
# AI policy: an assistant may explain an error message to you; it does not write the view or
# the labels. Under the company's rule below, rows of a Restricted table never go into one.
#
# **Tasks**
# - [ ] Open the supplied July database · 3 min
# - [ ] Mark each customer column: direct identifier, indirect identifier or neither · 8 min
# - [ ] Label each table with a classification level and a reason · 6 min
# - [ ] Write the analyst view with only the columns the purpose needs · 10 min
# - [ ] Run the analysts' three questions on the view and test that the identifiers are absent · 8 min
# - [ ] ✱ Stretch · Write a second view for the delivery team and list what it needs that the analysts do not

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
# ## 1 · The July database · 3 min
#
# The four tables as a correct load leaves them (the result of lab 4.1, supplied in
# `data/july/` so that this lab does not depend on yours).

# %%
j = U.july_db()
U.show("SELECT * FROM customers", j, n=3)

# %% [markdown]
# ## 2 · Which columns identify a person · 8 min
#
# - A **direct identifier** points to one person by itself: you could contact or find them.
# - An **indirect identifier** does not, alone, but combined with others can single a person out.
#   A customer number is one: it is a key that links every order back to the same person.
# - **Neither**: describes the person's choices or the record, and identifies no one.
#
# Under the Personal Data Protection Law, data from which a person can be identified, directly
# or indirectly, is personal data. Indirect identifiers are still personal data.
#
# ✏️ **Exercise 1** · One line per column: the column, a bar, `direct`, `indirect` or `neither`,
# then a semicolon and your reason.

# %%
IDENTIFIERS = """
-- BEGIN SOLUTION
customer_id      | indirect; a key that links all of one person's orders
joined_on        | indirect; an exact date, combined with region it narrows the group
region           | indirect; coarse alone, narrows the group with other columns
full_name        | direct; names the person
phone            | direct; reaches the person
email            | direct; reaches the person
birth_year       | indirect; with region and join date it can single a person out
marketing_opt_in | neither; a choice the person made, identifies no one
-- END SOLUTION
"""
U.check_pairs("l42_identifiers", IDENTIFIERS)

# %% [markdown]
# ## 3 · A level for each table · 6 min
#
# The company has adopted, as its own rule, the four levels of the national Data Classification
# Policy (written for public entities): Top Secret, Secret, Restricted and Public. Its rule:
#
# | Level | The company's rule |
# |---|---|
# | Top Secret, Secret | unauthorised disclosure has an exceptionally serious and irreparable effect, or a serious effect; none of the company's sales data reaches these |
# | Restricted | unauthorised disclosure has a limited negative effect on the company or on a person: personal data of customers, and records of individual transactions |
# | Public | disclosure has none of these effects: what the company has published, and what the data owner has labelled Public (the schema descriptions and the written business rules) |
# | not yet labelled | treated as Restricted until it is labelled |
#
# The store list (store, region, opening date, floor area) is printed on the company's public
# store pages.
#
# ✏️ **Exercise 2** · One line per table: the table, a bar, the level, a semicolon and the reason.

# %%
LABELS = """
-- BEGIN SOLUTION
stores      | Public; already published by the company
customers   | Restricted; personal data of customers
orders      | Restricted; individual transactions, each linked to one customer
order_lines | Restricted; the detail of individual transactions, linked to a customer through the order
-- END SOLUTION
"""
U.check_pairs("l42_labels", LABELS)

# %% [markdown]
# **Look at** order lines. No column in it names a person, and still it is Restricted: one join
# away, every line belongs to someone.
#
# ## 4 · The analyst view · 10 min
#
# The analysts' three questions:
#
# 1. How many customers joined in each region in July?
# 2. How many customers are in each birth decade (1950, 1960, ...)?
# 3. What was the net revenue of delivered orders in July, by the customer's region?
#
# ✏️ **Exercise 3** · Write `CREATE VIEW analyst_customers AS ...` with the fewest columns the
# three questions need. A birth decade answers question 2; the exact year is not needed. The
# customer number stays, because question 3 joins to orders: say so in a comment.

# %%
VIEW = """
-- BEGIN SOLUTION
CREATE OR REPLACE VIEW analyst_customers AS
SELECT customer_id,                          -- kept: the join to orders needs it; still personal data
       region,
       (birth_year // 10) * 10 AS birth_decade
FROM customers
-- END SOLUTION
"""
if not U._blank(VIEW):
    j.execute(VIEW)

# %% [markdown]
# ## 5 · The three questions, on the view only · 8 min
#
# ✏️ **Exercise 4** · Answer the three questions using `analyst_customers` and never `customers`.
# Question 1: columns `region`, `customers`, ordered by region.

# %%
SQL_Q1 = """
-- BEGIN SOLUTION
SELECT region, COUNT(*) AS customers
FROM analyst_customers
GROUP BY region
ORDER BY region
-- END SOLUTION
"""
U.check("l42_q1", SQL_Q1, con=j)

# %% [markdown]
# Question 2: columns `birth_decade`, `customers`, ordered by decade.

# %%
SQL_Q2 = """
-- BEGIN SOLUTION
SELECT birth_decade, COUNT(*) AS customers
FROM analyst_customers
GROUP BY birth_decade
ORDER BY birth_decade
-- END SOLUTION
"""
U.check("l42_q2", SQL_Q2, con=j)

# %% [markdown]
# Question 3: columns `region`, `net_revenue`, ordered by region. Follow the revenue rule
# (`data/revenue_rule.md`): delivered orders, lines with status `ok`, quantity times price minus
# the discount, an empty discount counting as 0. (The July file has no delivery attempts, so the
# order date stands in for the delivery date here.)

# %%
SQL_Q3 = """
-- BEGIN SOLUTION
SELECT a.region,
       SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM analyst_customers a
JOIN orders o      ON o.customer_id = a.customer_id
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status = 'delivered' AND l.line_status = 'ok'
GROUP BY a.region
ORDER BY a.region
-- END SOLUTION
"""
U.check("l42_q3", SQL_Q3, con=j)

# %% [markdown]
# The test: the view must not show a name, phone, e-mail, the exact birth year, the join date or
# the marketing choice. Run it.

# %%
U.test_view(j, "analyst_customers")

# %% [markdown]
# **Look at** what the view does not do: it does not anonymise. The customer number still links
# every analyst row to one person, so the view's output stays Restricted. A view limits what is
# exposed; it does not change the level.
#
# ## ✱ Stretch · The delivery team · optional
#
# The delivery team calls the customer of each cancelled order to offer a new slot. Write `delivery_contacts`
# and, in a comment, list what it needs that the analysts do not.

# %%
STRETCH = """
-- BEGIN SOLUTION
-- needs the phone and the name, which the analysts do not; does not need birth year or opt-in
CREATE OR REPLACE VIEW delivery_contacts AS
SELECT o.order_id, o.store_id, c.full_name, c.phone
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'cancelled'
-- END SOLUTION
"""
if not U._blank(STRETCH):
    j.execute(STRETCH)
    U.show("SELECT COUNT(*) AS rows_in_view FROM delivery_contacts", j)

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why is the customer number an indirect identifier and not "neither"?</summary>
#
# It points to one person across every table it appears in. With the orders and the region, a
# number can be traced back to a person; that is what indirect identification means.
# </details>
#
# <details><summary>2. Why replace the birth year with a decade?</summary>
#
# The question asks about decades. The exact year narrows the group without serving the
# purpose; a view that exposes only what the purpose needs is the minimum.
# </details>
#
# <details><summary>3. An analyst wants to paste the view's rows into a public chat assistant to
# get a chart. What does the company's rule say?</summary>
#
# The rows are Restricted: they stay out of public generative AI tools. The analyst can give the
# assistant the column names and ask for the chart code, then run it on the rows locally.
# </details>
#
# <details><summary>4. You built the view. Who should grant the analysts access to it?</summary>
#
# Not you. Segregation of duties: the person who builds the view does not also approve who reads
# it. The data protection officer, or the owner of the customer data, reviews the view's columns
# against the purpose and grants the access.
# </details>
#
# **Carry forward**: nothing; lab 4.3 starts from the company's database.
