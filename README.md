<!-- academy:title -->
# SQL and Relational Data

لغة SQL والبيانات العلائقية

Data & AI Foundations Track · SDAIA Academy · FND-DAT-101 · Level 100

Query relational data in SQL, predict the result before you run it, and prove the answer right against a known one

Participants query relational data in SQL and check that the answers are right. In an embedded analytical engine on a laptop they move from keys and constraints through joins, grouping and common table expressions to window functions. They predict results before running queries, catch the silent errors that joins and NULLs cause, and test assistant-written SQL against known answers. The capstone answers a stakeholder brief on an unseen dataset.

**Format:** Intensive: 4 teaching days and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/fnd-dat-101/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Explain the relational model: tables, keys, constraints, NULL and the grain of a table, given a six-table synthetic delivery schema | Awareness | an annotated schema with keys, cardinalities and grain matching the reference |
| LO2 | Identify the output of joins, grouping and NULL comparisons before running them, given small printed tables | Awareness | supervised AI-off check, eight of ten correct |
| LO3 | Write queries with filters, joins, grouping, subqueries and common table expressions that answer business questions, given a synthetic dataset of about a million order lines | Applied | a query file passing the automatic checker on 16 of 20 questions |
| LO4 | Apply window functions to rank rows, compare periods and compute running and moving totals, given daily order tables | Applied | queries matching reference outputs, each partition explained in a comment |
| LO5 | Implement a small schema with keys and constraints, load raw files into it and report rejected rows, given extracts with seeded defects | Applied | a definition script and a load log accounting for every rejected row |
| LO6 | Identify silent errors in assistant-written SQL, such as join fan-out, wrong grain and missing business rules, given ten generated queries and a revenue rule documented outside the schema | Awareness | a verification note judging each query, with a test result |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Tables, keys and grain | Tables, types, keys and constraints; Grain and cardinality; Normal forms, wide tables and embedded engines; Filters, sorting and expressions | [`slides/day1.html`](slides/day1.html) |
| Day 2 | One table, then two | CASE expressions and set operations; NULL and three-valued logic; Grouping and having; Inner, outer, semi and anti joins | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Combining safely, then windows | Join fan-out and double counting; Subqueries and common table expressions; Partitions, ranking, lag and lead; Running and moving aggregates | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Building and checking | Loading into constrained tables, and transactions; Views that limit what is exposed; Query plans and indexes; Testing queries against known answers | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone: the business orders brief |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**The grocery delivery company.** An online grocery and household goods delivery business in one city of five regions, dispatching from eight stores; every lab works on its synthetic six-table schema of about a million order lines from January to June 2026, with planted traps: delivery attempts that multiply rows, discounts left NULL, cancelled lines, closed days and a revenue rule finance keeps outside the schema. The capstone uses an unseen dataset from the company's business orders service; all data is synthetic and people appear only as roles and codes.

The company, its city, its stores, its products and its people are invented and described only
generically: regions are North, South, East, West and Central, stores are S01 to S08, customers
are codes such as C00042, and people appear only as roles (the head of commercial reporting, the
finance controller, the data protection officer, the analyst). Names, phone numbers and e-mail
addresses in the customer table are tokens that cannot identify, dial or reach anyone.

The data generator `labs/prepare_data.py` (Python standard library, seed 101) writes the six
tables in about ten seconds; the setup cell of every lab runs it when the tables are missing and
checks them against the digest in `labs/data/full.sha256`.

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Six tables and their keys | [`D1_1_tables_and_keys.ipynb`](labs/D1_1_tables_and_keys.ipynb) |
| 1.2 | Day 1 · Session 2 | The annotated schema | [`D1_2_annotated_schema.ipynb`](labs/D1_2_annotated_schema.ipynb) |
| 1.3 | Day 1 · Session 3 | One wide table, and what it repeats | [`D1_3_wide_table.ipynb`](labs/D1_3_wide_table.ipynb) |
| 1.4 | Day 1 · Session 4 | Questions 1 to 4, predicted first | [`D1_4_questions_1_to_4.ipynb`](labs/D1_4_questions_1_to_4.ipynb) |
| 2.1 | Day 2 · Session 1 | Questions 5 to 7: bands and sets | [`D2_1_questions_5_to_7.ipynb`](labs/D2_1_questions_5_to_7.ipynb) |
| 2.2 | Day 2 · Session 2 | Predict, then run: twelve NULL comparisons | [`D2_2_null_predictions.ipynb`](labs/D2_2_null_predictions.ipynb) |
| 2.3 | Day 2 · Session 3 | Questions 8 to 11: groups | [`D2_3_questions_8_to_11.ipynb`](labs/D2_3_questions_8_to_11.ipynb) |
| 2.4 | Day 2 · Session 4 | Questions 12 to 15: joins | [`D2_4_questions_12_to_15.ipynb`](labs/D2_4_questions_12_to_15.ipynb) |
| 3.1 | Day 3 · Session 1 | Questions 16 and 17: count once | [`D3_1_questions_16_and_17.ipynb`](labs/D3_1_questions_16_and_17.ipynb) |
| 3.2 | Day 3 · Session 2 | Questions 18 to 20, and the checker | [`D3_2_questions_18_to_20.ipynb`](labs/D3_2_questions_18_to_20.ipynb) |
| 3.3 | Day 3 · Session 3 | Window drills 1: top items per region | [`D3_3_window_drills_1.ipynb`](labs/D3_3_window_drills_1.ipynb) |
| 3.4 | Day 3 · Session 4 | Window drills 2: weeks and seven days | [`D3_4_window_drills_2.ipynb`](labs/D3_4_window_drills_2.ipynb) |
| 4.1 | Day 4 · Session 1 | Load the extracts and log every rejected row | [`D4_1_load_with_log.ipynb`](labs/D4_1_load_with_log.ipynb) |
| 4.2 | Day 4 · Session 2 | Label the tables and build the analyst view | [`D4_2_analyst_view.ipynb`](labs/D4_2_analyst_view.ipynb) |
| 4.3 | Day 4 · Session 3 | Read two plans and watch an index change one | [`D4_3_plans_and_indexes.ipynb`](labs/D4_3_plans_and_indexes.ipynb) |
| 4.4 | Day 4 · Session 4 | Ten generated queries against hand-checked answers | [`D4_4_ten_generated_queries.ipynb`](labs/D4_4_ten_generated_queries.ipynb) |
<!-- /academy:labs -->

## Capstone

A ten-question stakeholder brief on a new synthetic dataset, answered in a repository of tested SQL with a note on assumptions, plus a timed AI-off check and a live adaptation of one query to a changed question.

The brief comes from the head of the company's business orders service, a line the labs never
touch: seven new tables, ten questions and a rule on prices kept outside the schema
(`labs/capstone/`).

**Submission:** Individual. A public GitHub repository link holding the answers to the ten questions of the business orders brief (labs/capstone/): one SQL file per question with a comment on its grain, a pytest test per question against a hand-checked fixture, the assumptions note and the log of any generated SQL and how it was checked, with the history kept. On the capstone day: the timed AI-off check, then five minutes of live adaptation of one query to a changed question and two minutes of questions on the assumptions note.

| Rubric criterion (capstone repository) | Weight |
|---|---|
| Correct answers: the ten queries return the trainer's key on the full business orders data | 35 |
| Tests: each query has a pytest test against a small fixture whose expected rows were worked out by hand, and the tests pass | 20 |
| Grain: each query states the grain of its result and of every table it joins, and no total is counted twice | 15 |
| Assumptions note: every business rule of the brief stated, applied and traced to the query that uses it | 15 |
| Verification log: every query an assistant wrote or changed is recorded with the test that caught or passed it | 10 |
| Minimal exposure: no answer returns a personal-data column the question does not need | 5 |

## Assessment

| Component | Weight |
|---|---|
| Lab query files, auto-checked | 30% |
| Timed AI-off check of ten questions | 30% |
| Capstone repository, rubric-scored | 30% |
| Live query adaptation | 10% |

- **Passing:** 70% overall and at least 60% on the timed check.
- **Authenticity:** A supervised timed check without assistance, and a live session in which the participant adapts a capstone query to a new question.
- **Certificate:** completion with assessed work.
- The lab query files are the five assessed lab threads, 6% each: the annotated schema (lab 1.2), the twenty questions (labs 1.4 to 3.2, checked in lab 3.2), the window drills (labs 3.3 and 3.4), the definition script and load log (lab 4.1) and the verification note (lab 4.4).
- **AI policy:** AI-off in the pre-work drills, the prediction exercises and the timed check. AI-tutor in labs, explaining errors without writing queries. AI-full in the verification lab and the capstone.
- The timed check's items and the capstone's answer key are kept by the Academy, outside this repository.

## Responsible use

Covers classification and minimisation: participants mark the personal-data columns of a synthetic customer table and build a view that exposes only what an analyst needs. All data is synthetic.

Only the schema and synthetic data are ever given to an assistant in this course. The
classification levels are used in lab 4.2 as the company's own rule, modelled on the national
policy, which is written for public entities.

## How the course is organised

Four teaching days of four one-hour sessions (about 25 minutes of ideas, then a lab of 30 or 35
minutes), then a capstone day. Minutes: instruction 420, labs 540, guided self-study 420 (pre-work
120, after Days 1 and 2 30 each, after Day 3 60, the capstone repository 120, the tracked
follow-up task 60), assessment 120 (the timed check 40, live adaptations of 5 minutes for 16
participants), capstone 300 (opening 15, final preparation 120, questions on the assumptions
note 2 minutes and changeovers 1 minute for 16 participants, peer review 50, trainer review 42,
follow-up brief 25).

## Prerequisites

- Comfortable with spreadsheets: filters, sorting and simple formulas
- No programming experience required

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Embedded analytical SQL engine:** DuckDB, SQLite
- **Query checking:** pytest comparing result sets, the Academy's query grader
- **Assistant for the text-to-SQL exercises:** a locally served open-weight model, any approved assistant
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

### National references

- [Personal Data Protection Law (SDAIA), English text](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Minimum Personal Data Determination Guideline, version 1.0, August 2024 (SDAIA)](https://sdaia.gov.sa/Documents/MinmumPDGuideline.pdf)
- [Data Classification Policy, version 1 (National Data Management Office, SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
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
<!-- /academy:sources -->

### National references

- Personal Data Protection Law (PDPL): data minimisation, in the view exercise: https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf (Article 11 on collecting the minimum necessary; read in English, the Arabic file's text could not be extracted). The Minimum Personal Data Determination Guideline (version 1.0, August 2024) explains the principle: https://sdaia.gov.sa/Documents/MinmumPDGuideline.pdf
- NDMO Data Classification Policy: levels used to label tables: https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf (version 1, the version linked from SDAIA's regulations page on 25 November 2026: levels Top Secret, Secret, Restricted and Public)
- SDAIA Data & AI Academic Programs Standards Framework (2026): DM-Relational and DM-Querying units: https://sdaia.gov.sa/en/MediaCenter/KnowledgeCenter/ResearchLibrary/Academic-Programs-Standards-Framework-Q3.pdf (Second Version, September 2026)
