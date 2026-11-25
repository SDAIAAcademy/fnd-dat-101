---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/index.html"
---

# SQL and Relational Data

لغة SQL والبيانات العلائقية

Data & AI Foundations Track · 4 teaching days + capstone day · 30 hours · Level 100

Query relational data in SQL, predict the result before you run it, and prove the answer right against a known one

Participants query relational data in SQL and check that the answers are right. In an embedded analytical engine on a laptop they move from keys and constraints through joins, grouping and common table expressions to window functions. They predict results before running queries, catch the silent errors that joins and NULLs cause, and test assistant-written SQL against known answers. The capstone answers a stakeholder brief on an unseen dataset.

**Who it is for:** Beginners. Anyone starting technical data or AI work, including future analysts, data scientists, data engineers and AI engineers who can code but have not yet worked with messy real data.

**Format:** Intensive: 4 teaching days and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**The grocery delivery company.** An online grocery and household goods delivery business in one city of five regions, dispatching from eight stores; every lab works on its synthetic six-table schema of about a million order lines from January to June 2026, with planted traps: delivery attempts that multiply rows, discounts left NULL, cancelled lines, closed days and a revenue rule finance keeps outside the schema. The capstone uses an unseen dataset from the company's business orders service; all data is synthetic and people appear only as roles and codes.

## The course

### Day 1: Tables, keys and grain

Slides: https://sdaiaacademy.github.io/fnd-dat-101/slides/day1.md

- **Session 1: Tables, types, keys and constraints**
  - Name the type and the role of each column of a table
  - Test a candidate key with a counting query
  - Read the message a database gives when a constraint refuses a row
  - [Lab 1.1: Six tables and their keys (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_1_tables_and_keys.ipynb)
- **Session 2: Grain and cardinality**
  - State the grain of a table in one sentence
  - Confirm a grain with a counting query
  - Measure a one-to-many relationship and name its maximum
  - [Lab 1.2: The annotated schema (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_2_annotated_schema.ipynb)
- **Session 3: Normal forms, wide tables and embedded engines**
  - Explain the repetition that normal forms remove
  - Build a wide analytical table from a join and name its risks
  - Contrast an embedded engine with a client-server database
  - [Lab 1.3: One wide table, and what it repeats (30 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_3_wide_table.ipynb)
- **Session 4: Filters, sorting and expressions**
  - Filter rows on text patterns and date ranges
  - Sort with a tie-breaker and keep the top rows
  - Compute a value per row with an expression that handles a NULL
  - [Lab 1.4: Questions 1 to 4, predicted first (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_4_questions_1_to_4.ipynb)

### Day 2: One table, then two

Slides: https://sdaiaacademy.github.io/fnd-dat-101/slides/day2.md

- **Session 1: CASE expressions and set operations**
  - Write a CASE expression that sorts rows into bands
  - Count by condition with CASE inside an aggregate
  - Combine two result sets with UNION, INTERSECT or EXCEPT
  - [Lab 2.1: Questions 5 to 7: bands and sets (30 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_1_questions_5_to_7.ipynb)
- **Session 2: NULL and three-valued logic**
  - Predict the rows a comparison with NULL keeps
  - Use IS NULL, COALESCE and IS DISTINCT FROM on purpose
  - Explain why NOT IN with a NULL returns no rows
  - [Lab 2.2: Predict, then run: twelve NULL comparisons (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_2_null_predictions.ipynb)
- **Session 3: Grouping and having**
  - Predict the number of rows a GROUP BY returns
  - Choose between WHERE and HAVING for a condition
  - Count distinct values inside a group
  - [Lab 2.3: Questions 8 to 11: groups (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_3_questions_8_to_11.ipynb)
- **Session 4: Inner, outer, semi and anti joins**
  - Predict the rows an inner and a left join return on small tables
  - Find rows without a partner with an anti join
  - Keep rows that have a partner without multiplying them, with a semi join
  - [Lab 2.4: Questions 12 to 15: joins (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_4_questions_12_to_15.ipynb)

### Day 3: Combining safely, then windows

Slides: https://sdaiaacademy.github.io/fnd-dat-101/slides/day3.md

- **Session 1: Join fan-out and double counting**
  - Detect fan-out by counting rows before and after a join
  - Aggregate to the right grain before joining
  - Explain a wrong total from the grain of each table it joined
  - [Lab 3.1: Questions 16 and 17: count once (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_1_questions_16_and_17.ipynb)
- **Session 2: Subqueries and common table expressions**
  - Use a subquery in WHERE and in FROM
  - Write a query as a chain of common table expressions
  - Check each step of a chain before trusting the last
  - [Lab 3.2: Questions 18 to 20, and the checker (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_2_questions_18_to_20.ipynb)
- **Session 3: Partitions, ranking, lag and lead**
  - Write a window with a partition and an ordering
  - Choose between ROW_NUMBER, RANK and DENSE_RANK at ties
  - Compare a row with the one before it using LAG
  - [Lab 3.3: Window drills 1: top items per region (30 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_3_window_drills_1.ipynb)
- **Session 4: Running and moving aggregates**
  - Compute a running total that restarts in each partition
  - Compute a week-on-week change with LAG over weekly totals
  - Choose a ROWS or a RANGE frame when days are missing
  - [Lab 3.4: Window drills 2: weeks and seven days (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_4_window_drills_2.ipynb)

### Day 4: Building and checking

Slides: https://sdaiaacademy.github.io/fnd-dat-101/slides/day4.md

- **Session 1: Loading into constrained tables, and transactions**
  - Write table definitions with keys, foreign keys and checks
  - Load a raw file through a staging table and record each rejected row with its reason
  - Group inserts, updates and deletes in a transaction and roll back on a failed check
  - [Lab 4.1: Load the extracts and log every rejected row (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_1_load_with_log.ipynb)
- **Session 2: Views that limit what is exposed**
  - Mark the personal-data columns of a table
  - Label tables with classification levels under a stated rule
  - Build a view that exposes only what an analyst needs, and test it
  - [Lab 4.2: Label the tables and build the analyst view (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_2_analyst_view.ipynb)
- **Session 3: Query plans and indexes**
  - Read the operators of a query plan from the bottom up
  - Find where a filter is applied in a plan
  - Predict when an index changes a plan and when it does not
  - [Lab 4.3: Read two plans and watch an index change one (30 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_3_plans_and_indexes.ipynb)
- **Session 4: Testing queries against known answers**
  - Build a small fixture and work out the expected answer by hand
  - Write a test that compares a query's result with the expected rows
  - Classify a failing generated query: fan-out, wrong grain or a missing business rule
  - [Lab 4.4: Ten generated queries against hand-checked answers (35 min)](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_4_ten_generated_queries.ipynb)

### Capstone: Capstone: the business orders brief

Slides: https://sdaiaacademy.github.io/fnd-dat-101/slides/capstone.md

## Capstone

A ten-question stakeholder brief on a new synthetic dataset, answered in a repository of tested SQL with a note on assumptions, plus a timed AI-off check and a live adaptation of one query to a changed question

**What you submit:** Individual. A public GitHub repository link holding the answers to the ten questions of the business orders brief (labs/capstone/): one SQL file per question with a comment on its grain, a pytest test per question against a hand-checked fixture, the assumptions note and the log of any generated SQL and how it was checked, with the history kept. On the capstone day: the timed AI-off check, then five minutes of live adaptation of one query to a changed question and two minutes of questions on the assumptions note.

**Rubric:**

- Correct answers: the ten queries return the trainer's key on the full business orders data: 35%
- Tests: each query has a pytest test against a small fixture whose expected rows were worked out by hand, and the tests pass: 20%
- Grain: each query states the grain of its result and of every table it joins, and no total is counted twice: 15%
- Assumptions note: every business rule of the brief stated, applied and traced to the query that uses it: 15%
- Verification log: every query an assistant wrote or changed is recorded with the test that caught or passed it: 10%
- Minimal exposure: no answer returns a personal-data column the question does not need: 5%

## Outcomes

- **LO1** Explain the relational model: tables, keys, constraints, NULL and the grain of a table, given a six-table synthetic delivery schema (Awareness) Evidence: an annotated schema with keys, cardinalities and grain matching the reference
- **LO2** Identify the output of joins, grouping and NULL comparisons before running them, given small printed tables (Awareness) Evidence: supervised AI-off check, eight of ten correct
- **LO3** Write queries with filters, joins, grouping, subqueries and common table expressions that answer business questions, given a synthetic dataset of about a million order lines (Applied) Evidence: a query file passing the automatic checker on 16 of 20 questions
- **LO4** Apply window functions to rank rows, compare periods and compute running and moving totals, given daily order tables (Applied) Evidence: queries matching reference outputs, each partition explained in a comment
- **LO5** Implement a small schema with keys and constraints, load raw files into it and report rejected rows, given extracts with seeded defects (Applied) Evidence: a definition script and a load log accounting for every rejected row
- **LO6** Identify silent errors in assistant-written SQL, such as join fan-out, wrong grain and missing business rules, given ten generated queries and a revenue rule documented outside the schema (Awareness) Evidence: a verification note judging each query, with a test result

## Tools

- **Embedded analytical SQL engine:** DuckDB, SQLite
- **Query checking:** pytest comparing result sets, the Academy's query grader
- **Assistant for the text-to-SQL exercises:** a locally served open-weight model, any approved assistant

## Prerequisites

- Comfortable with spreadsheets: filters, sorting and simple formulas
- No programming experience required

## Sources

### National references

- [Personal Data Protection Law (SDAIA), English text](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Minimum Personal Data Determination Guideline, version 1.0, August 2024 (SDAIA)](https://sdaia.gov.sa/Documents/MinmumPDGuideline.pdf)
- [Data Classification Policy, version 1 (National Data Management Office, SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [Generative Artificial Intelligence Guidelines for Government, 2025 (SDAIA), section 3.5 Privacy and Security](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
- [Data & AI Academic Programs Standards Framework, Second Version, September 2026 (SDAIA)](https://sdaia.gov.sa/en/MediaCenter/KnowledgeCenter/ResearchLibrary/Academic-Programs-Standards-Framework-Q3.pdf)

### Engines and tools

- [DuckDB: Why DuckDB](https://duckdb.org/why_duckdb)
- [DuckDB 2.0 documentation: constraints](https://duckdb.org/docs/stable/sql/constraints)
- [DuckDB 2.0 documentation: window functions](https://duckdb.org/docs/stable/sql/functions/window_functions)
- [DuckDB 2.0 documentation: EXPLAIN](https://duckdb.org/docs/stable/guides/meta/explain)
- [DuckDB 2.0 documentation: indexes](https://duckdb.org/docs/2.0/sql/indexes.html)
- [DuckDB 2.0 documentation: CREATE VIEW](https://duckdb.org/docs/stable/sql/statements/create_view)
- [DuckDB 2.0 documentation: transaction management](https://duckdb.org/docs/stable/sql/statements/transactions)
- [SQLite: SQLite Is Serverless](https://www.sqlite.org/serverless.html)
- [SQLite: EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [pytest documentation](https://docs.pytest.org/en/stable/)

---

SDAIA Academy · Data & AI Foundations Track · SQL and Relational Data

Course version 2027.1.0 · engine 1.0.0 · built 2026-11-25 · commit 65f9e39
