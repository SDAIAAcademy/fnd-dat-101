# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Lab 4.4 · Ten generated queries against hand-checked answers
#
# Day 4 · Session 4 (Testing queries against known answers) · 35 min.
#
# Ten revenue queries, written the way SQL generated from a question often comes out, are about
# to go into a report. Before anyone reads the report, you test the ten queries: you work out each
# answer by hand on the mini tables, small enough to check on paper, run every query against them,
# and classify each failure as fan-out, wrong grain or a missing business rule.
#
# Where the queries come from: the ten in `data/verification/generated_queries.sql` were written
# for this course to reproduce mistakes that SQL generated from a question often contains. No
# model produced them. The method is the one you would use on real generated SQL.
#
# AI policy: AI-off for the expected answers: they are worth something only if you worked them
# out yourself. AI-full for the stretch, with the schema only. The queries under test are
# generated-style by design.
#
# **Tasks**
# - [ ] Read the revenue rule and the ten questions · 5 min
# - [ ] Work out the expected answers on the mini tables by hand · 10 min
# - [ ] Run the ten queries through the tests · 8 min
# - [ ] Classify each failure: fan-out, grain or a missing rule · 7 min
# - [ ] Write the verification note with each test result · 5 min
# - [ ] ✱ Stretch · Ask an approved assistant for the same ten questions, given only the schema, and run its queries through the same tests

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
# ## 1 · The rule and the questions · 5 min
#
# Read `data/revenue_rule.md` again: six points, and the fifth (the date of revenue is the date
# of the successful delivery) is the one most often missed. The ten questions:

# %%
print(Path("data/revenue_rule.md").read_text(encoding="utf-8"))
for key, sql in U.generated_queries().items():
    print(key, sql.splitlines()[0].removeprefix("-- question: "))

# %% [markdown]
# ## 2 · Expected answers, by hand · 10 min
#
# The four tables you need, printed. Work on paper, the assistant closed. Three of the questions
# are counts and take a minute; the revenue ones are where the time goes. Start with the
# delivered orders and their `ok` lines, then sort them by the date of the delivered attempt.

# %%
U.show("SELECT * FROM orders", m, n=10)
U.show("SELECT * FROM order_lines", m, n=20)
U.show("SELECT * FROM deliveries", m, n=12)

# %% [markdown]
# ✏️ **Exercise 1** · One line per question: the key, a bar, the answer. Amounts with two
# decimals; for v10, the customer and the amount separated by a comma.

# %%
EXPECTED = """
-- BEGIN SOLUTION
v01 | 182.40
v02 | 48.30
v03 | 6
v04 | 30.40
v05 | 95.60
v06 | 4
v07 | 86.80
v08 | 1
v09 | 182.40
v10 | C003, 87.60
-- END SOLUTION
"""
U.check_pairs("l44_expected", EXPECTED)

# %% [markdown]
# ## 3 · Run the tests · 8 min
#
# Each query runs on the mini tables and its first row is compared with your answer.

# %%
results = U.run_tests(EXPECTED, m)

# %% [markdown]
# ## 4 · Why each failure fails · 7 min
#
# Read each failing query against the rule and against the tables. Three kinds of failure:
#
# - **fan-out**: a join repeats rows, so a sum counts some lines more than once;
# - **grain**: the query computes at the wrong level, for example per line when the question is
#   per order;
# - **missing rule**: the query is well formed but leaves out a point of the revenue rule.
#
# ✏️ **Exercise 2** · One line per query: the key, a bar, `ok`, `fan-out`, `grain` or
# `missing rule`, then a semicolon and the reason in a few words.

# %%
VERDICTS = """
-- BEGIN SOLUTION
v01 | fan-out; joins every delivery attempt, so orders with a failed attempt count twice or three times
v02 | missing rule; books revenue on the order date instead of the delivered attempt
v03 | ok
v04 | grain; averages lines, the question is per order
v05 | missing rule; leaves the discount out
v06 | ok
v07 | missing rule; counts the returned order as revenue
v08 | ok
v09 | ok
v10 | fan-out; the same repeated attempts inflate the top customer's total
-- END SOLUTION
"""
U.check_pairs("l44_verdicts", VERDICTS)

# %% [markdown]
# **Look at** v10: it names the right customer with the wrong amount. A test that checked only
# the customer would have passed it.
#
# ## 5 · The verification note · 5 min
#
# The note goes with the report: each query, your expected answer, what it returned, the test
# result and your judgement. Run the cell; it writes `answers/verification_note.md`.

# %%
note = U.write_note(results, VERDICTS)
print(note.read_text(encoding="utf-8"))

# %% [markdown]
# ## ✱ Stretch · Real generated SQL · optional
#
# Give an approved assistant the schema only (the column names in `data/mini/*.csv` headers and
# the ten questions, nothing else: no rows), ask for the ten queries, and paste them below in the
# same `-- name: v01` format. They run through the same tests. Do not paste the revenue rule
# first: you want to see what it does without it. Then paste the rule and ask again.

# %%
ASSISTANT_SQL = """
-- name: v01
"""
mine = {k: v for k, v in U.read_answers_text(ASSISTANT_SQL).items() if not U._blank(v)}
if mine:
    U.run_tests(EXPECTED, m, queries=mine)
else:
    print("no assistant queries pasted: nothing to test")

# %% [markdown]
# ## Check yourself
#
# <details><summary>1. Why the mini tables and not the full database?</summary>
#
# On the full data you cannot know the right answer except by running another query, which may
# share the same mistake. On eight orders you can check by hand, so the expected answer is
# independent of any SQL.
# </details>
#
# <details><summary>2. v09 passed. Does that make it correct on the full data?</summary>
#
# It makes it consistent with the rule on these cases, which include a failed attempt, a
# returned order, a cancelled line and an empty discount. A case the fixture lacks, such as two
# successful attempts, is not tested: add it to the fixture if the data can have it.
# </details>
#
# <details><summary>3. Four of ten passed. What do you write in the report?</summary>
#
# That six of the figures were wrong and why, with the verification note attached, and the
# corrected figures from queries that pass. Generated SQL is a draft until it passes a test
# against answers someone worked out by hand.
# </details>
#
# <details><summary>4. At work, a colleague generates queries like these with an assistant. Should the same colleague also write the expected answers?</summary>
#
# No. Segregation of duties: the person who produced a query does not also produce the answer it
# is tested against, or one misunderstanding of the rule passes both. You worked them out; a
# reviewer signs the verification note.
# </details>
#
# **Carry forward**: the method. The capstone asks for a test per question against a fixture you
# check by hand.
