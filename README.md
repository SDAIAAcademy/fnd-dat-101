<!-- academy:title -->
# SQL and Relational Data

لغة SQL والبيانات العلائقية

Data & AI Foundations Track · SDAIA Academy · FND-DAT-101 · Level 100

REPLACE: one line under the title: what participants can do after the course

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
| Day 1 | REPLACE: the theme of this unit, in a few words | REPLACE: the title of Session 1; REPLACE: the title of Session 2; REPLACE: the title of Session 3; REPLACE: the title of Session 4 | [`slides/day1.html`](slides/day1.html) |
| Day 2 | REPLACE: the theme of this unit, in a few words | REPLACE: the title of Session 1; REPLACE: the title of Session 2; REPLACE: the title of Session 3; REPLACE: the title of Session 4 | [`slides/day2.html`](slides/day2.html) |
| Day 3 | REPLACE: the theme of this unit, in a few words | REPLACE: the title of Session 1; REPLACE: the title of Session 2; REPLACE: the title of Session 3; REPLACE: the title of Session 4 | [`slides/day3.html`](slides/day3.html) |
| Day 4 | REPLACE: the theme of this unit, in a few words | REPLACE: the title of Session 1; REPLACE: the title of Session 2; REPLACE: the title of Session 3; REPLACE: the title of Session 4 | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | REPLACE: what participants build in lab 1.1 | [`D1_1.ipynb`](labs/D1_1.ipynb) |
| 1.2 | Day 1 · Session 2 | REPLACE: what participants build in lab 1.2 | [`D1_2.ipynb`](labs/D1_2.ipynb) |
| 1.3 | Day 1 · Session 3 | REPLACE: what participants build in lab 1.3 | [`D1_3.ipynb`](labs/D1_3.ipynb) |
| 1.4 | Day 1 · Session 4 | REPLACE: what participants build in lab 1.4 | [`D1_4.ipynb`](labs/D1_4.ipynb) |
| 2.1 | Day 2 · Session 1 | REPLACE: what participants build in lab 2.1 | [`D2_1.ipynb`](labs/D2_1.ipynb) |
| 2.2 | Day 2 · Session 2 | REPLACE: what participants build in lab 2.2 | [`D2_2.ipynb`](labs/D2_2.ipynb) |
| 2.3 | Day 2 · Session 3 | REPLACE: what participants build in lab 2.3 | [`D2_3.ipynb`](labs/D2_3.ipynb) |
| 2.4 | Day 2 · Session 4 | REPLACE: what participants build in lab 2.4 | [`D2_4.ipynb`](labs/D2_4.ipynb) |
| 3.1 | Day 3 · Session 1 | REPLACE: what participants build in lab 3.1 | [`D3_1.ipynb`](labs/D3_1.ipynb) |
| 3.2 | Day 3 · Session 2 | REPLACE: what participants build in lab 3.2 | [`D3_2.ipynb`](labs/D3_2.ipynb) |
| 3.3 | Day 3 · Session 3 | REPLACE: what participants build in lab 3.3 | [`D3_3.ipynb`](labs/D3_3.ipynb) |
| 3.4 | Day 3 · Session 4 | REPLACE: what participants build in lab 3.4 | [`D3_4.ipynb`](labs/D3_4.ipynb) |
| 4.1 | Day 4 · Session 1 | REPLACE: what participants build in lab 4.1 | [`D4_1.ipynb`](labs/D4_1.ipynb) |
| 4.2 | Day 4 · Session 2 | REPLACE: what participants build in lab 4.2 | [`D4_2.ipynb`](labs/D4_2.ipynb) |
| 4.3 | Day 4 · Session 3 | REPLACE: what participants build in lab 4.3 | [`D4_3.ipynb`](labs/D4_3.ipynb) |
| 4.4 | Day 4 · Session 4 | REPLACE: what participants build in lab 4.4 | [`D4_4.ipynb`](labs/D4_4.ipynb) |
<!-- /academy:labs -->

## Capstone

A ten-question stakeholder brief on a new synthetic dataset, answered in a repository of tested SQL with a note on assumptions, plus a timed AI-off check and a live adaptation of one query to a changed question

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

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

- REPLACE: every source the course cites, with its address, in course.json under "sources"; this list is written from there
<!-- /academy:sources -->

### National references

- Personal Data Protection Law (PDPL): data minimisation, in the view exercise: REPLACE: the address of the official text
- NDMO Data Classification Policy: levels used to label tables: REPLACE: the address of the official text
- SDAIA Data & AI Academic Programs Standards Framework (2026): DM-Relational and DM-Querying units: REPLACE: the address of the official text
