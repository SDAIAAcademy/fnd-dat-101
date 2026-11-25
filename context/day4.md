---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/slides/day4.html"
---

# SQL and Relational Data

## Day 4: Building and checking

Constraints that refuse, views that limit, plans that explain, tests that prove

#### [day4#title] Building and checking

*SDAIA Academy · SQL and Relational Data*

Day 4: Constraints that refuse, views that limit, plans that explain, tests that prove

Data & AI Foundations Track · 4 teaching days + capstone day · 4 sessions · 4 labs · FND-DAT-101

#### [day4#agenda] Building and checking

*Today*

- **Session 1 · Loading into constrained tables, and transactions**: Stage the raw file, sort out what the constraints would refuse, load the rest in one transaction, account for every row
- **Session 2 · Views that limit what is exposed**: A view gives each reader the columns and rows the purpose needs, and no more
- **Session 3 · Query plans and indexes**: EXPLAIN shows how the engine will run a query; an index changes a lookup, rarely a scan of everything
- **Session 4 · Testing queries against known answers**: A query is right when it matches answers you worked out by hand on data small enough to check

#### [day4#review-day3] Which ranking gives the tied products the same rank, and leaves no gap after them?

*Review of Day 3*

**Question:** A bakery ranks products by units sold. Two products tie for second place. The next product should be third.

- A. ROW_NUMBER()
- B. DENSE_RANK()
- C. RANK()
- D. NTILE(3)

### Session 1: Loading into constrained tables, and transactions

#### [day4#s1] Loading into constrained tables, and transactions

*Session 1*

- Write table definitions with keys, foreign keys and checks
- Load a raw file through a staging table and record each rejected row with its reason
- Group inserts, updates and deletes in a transaction and roll back on a failed check

#### [day4#constraints-refuse] A constraint is a rule the database checks on every row, every time

*Constraints*

| Constraint | Refuses | Returns desk example |
| --- | --- | --- |
| `PRIMARY KEY` | a repeated or empty key | a second T2 |
| `NOT NULL` | an empty value | a return with no date |
| `REFERENCES` | a value with no row on the one side | reason R9, which does not exist |
| `CHECK` | a value outside a stated condition | a refund below zero |

> **What goes wrong.** A rule written only in a document is checked by nobody. Written as a constraint, it holds for every program that writes to the table.

#### [day4#stage-first] Stage the raw file as text, give each bad row a reason, then insert the rest

*Step by step*

1. **1 · Stage** every row as text, numbered in file order
2. **2 · Reject** a rule gives each bad row one reason
3. **3 · Insert** the rest, cast to the table's types
4. **4 · Log** read = loaded + rejected

> **Takeaway.** Straight into a constrained table, the load stops at the first bad row. Staged, you see them all at once.

#### [day4#reject-rule] CASE gives each row the first reason that applies, so the counts add up

*A reject rule*

```sql
-- file: returns desk
SELECT row_no, return_id,
  CASE
    WHEN return_id = '' THEN 'missing key'
    WHEN ROW_NUMBER() OVER (
      PARTITION BY return_id
      ORDER BY row_no) > 1 THEN 'duplicate key'
    WHEN reason_code NOT IN
      (SELECT reason_code FROM reasons)
      THEN 'unknown reason'
    WHEN TRY_CAST(refund AS DECIMAL(8,2)) < 0
      THEN 'negative refund'
  END AS reason
FROM stg_returns
```

| row | return_id | reason |
| --- | --- | --- |
| 1 | T6 |  |
| 2 | T6 | duplicate key |
| 3 | (empty) | missing key |
| 4 | T7 | unknown reason |
| 5 | T8 | negative refund |
| 6 | T9 |  |

The returns desk (`_tools/slide_examples.py`, stage-reject).

#### [day4#transaction] A transaction keeps all its changes or none of them

*Transactions*

```sql
-- file: returns desk
BEGIN TRANSACTION;
INSERT INTO returns VALUES
  ('T10', 'O-A30', 'R1', 4.00, '2026-05-10'),
  ('T11', 'O-A31', 'R9', 2.00, '2026-05-10'),
  ('T12', 'O-A32', 'R2', 6.00, '2026-05-10');
-- refused: R9 is not a reason
ROLLBACK;
```

**5 → 5** rows of returns, before and after

T10 and T12 were valid, and they are not kept either. Then `COMMIT` makes every change of a transaction permanent at once.

> **What goes wrong.** Without a transaction, a load that fails halfway leaves orders without their lines, and July's reports count orders with no revenue.

#### [day4#load-log] Every row read is either loaded or rejected with a reason

*The load log*

| File | Read | Loaded | Rejected |
| --- | --- | --- | --- |
| returns | 6 | 2 | 4 |

Rejected by reason: missing key 1 · duplicate key 1 · unknown reason 1 · negative refund 1

- The log is the evidence that nothing was lost **silently**
- A rejection upstream changes counts downstream: the items of a rejected return are rejected too

#### [day4#check-load-log] What does this load log tell you?

*Checkpoint*

**Question:** A clinic's appointments file: read 500, loaded 480, rejected 15 (12 unknown patient, 3 invalid date).

- A. The load is complete and every row is accounted for
- B. The transaction rolled back 15 rows
- C. Five rows are unaccounted for
- D. The file was loaded twice

#### [day4#lab-4-1] Load the extracts and log every rejected row

Lab 4.1 · 35 min

Define three constrained tables, stage the defective July extracts, give each bad row a reason, and log every file as loaded plus rejected

[D4_1_load_with_log.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_1_load_with_log.ipynb)

- [ ] Write the three table definitions with their keys and checks (10 min)
- [ ] Load the three extracts into all-text staging tables (4 min)
- [ ] Write the reject rules for orders and order lines, each with a reason (10 min)
- [ ] Insert the valid rows inside a transaction and write the load log (8 min)
- [ ] Check that read equals loaded plus rejected for every file (3 min)
- [ ] ✱ Stretch: Correct one rejected order with an UPDATE inside a transaction, roll it back and confirm nothing changed

### Session 2: Views that limit what is exposed

#### [day4#s2] Views that limit what is exposed

*Session 2*

- Mark the personal-data columns of a table
- Label tables with classification levels under a stated rule
- Build a view that exposes only what an analyst needs, and test it

#### [day4#identifiers] A column is personal data if it can identify a person, alone or with others

*Personal data*

- **Direct identifier.** Points to one person by itself: a name, a phone number, an e-mail address.
- **Indirect identifier.** Narrows the group when combined: a date, an area, a key that links all of one person's records.
- **Neither.** Describes a choice or the record, and identifies no one on its own.

The returns desk's callback list: `return_id`, `caller_name`, `caller_phone`, `area`, `received_on`, `callback_ok`. Which is which?

The Personal Data Protection Law treats data that identifies a person directly or indirectly as personal data.

#### [day4#minimum-necessary] Give each reader the columns the purpose needs, and no more

*Minimisation*

- The law asks that personal data be **limited to the minimum necessary** for the purpose (PDPL, Article 11, paragraph 3)
- The Minimum Personal Data guideline adds: restrict **access rights** to what each role actually needs
- A purpose is a question: "how many returns per area each week" needs no name and no phone
- An exact date can often become a week or a month; an exact year, a decade

> **What goes wrong.** "Give them a copy without the names" makes a second table to secure, forget and leak. A view is not a copy.

#### [day4#classification-levels] A level says how much harm disclosure would do, and so how the data is handled

*Classification*

| Level | Impact | Unauthorised disclosure has |
| --- | --- | --- |
| Top Secret | high | an exceptionally serious and irreparable effect |
| Secret | medium | a serious effect |
| Restricted | low | a limited negative effect, including on an individual; examples include personally identifiable information and detailed statements of individual transactions |
| Public | none | none of these effects |

The four levels of the national Data Classification Policy, written for public entities. Data not yet classified is treated as Restricted until it is. In the labs, the grocery delivery company has adopted the levels as its own rule.

#### [day4#view] A view is a stored query: readers see its columns, never the table behind it

*Views*

```sql
-- file: returns desk
CREATE VIEW returns_for_analysts AS
SELECT return_id,                              -- kept: joins to items; still personal data
       area,
       DATE_TRUNC('week', received_on) AS received_week
FROM callback_list;                            -- no name, no phone, no exact date

-- the test: none of these may appear
DESCRIBE returns_for_analysts;
```

> **Grant the view, not the table.** The analysts' role reads the view; the table stays with the desk.

#### [day4#genai-rule] Restricted rows never go into a generative AI tool; the schema can

*Responsible use*

- **Can go in.** What the company has labelled Public: column names and types, the written business rules, an error message, a query with no values from the data.
- **Stays out.** Rows of a Restricted table, a view's output, a sample "just to show the shape", a screenshot of a result.

> **Rule.** Only Public data goes into a generative AI tool. Which descriptions count as Public is the company's own labelling, written down before anyone relies on it.

#### [day4#check-view] Which view gives the analysts what they need, and no more?

*Checkpoint*

**Question:** A gym's members table: member_id, full_name, phone, birth_date, branch, joined_on. The analysts count members per branch and per age band.

- A. member_id, branch, age band
- B. member_id, branch, birth_date
- C. member_id, branch, birth_date, joined_on
- D. a copy of the table without full_name

#### [day4#lab-4-2] Label the tables and build the analyst view

Lab 4.2 · 35 min

Mark the personal-data columns, label each table under the company's rule, and build a view the analysts can query without names, phones or e-mail

[D4_2_analyst_view.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_2_analyst_view.ipynb)

- [ ] Open the supplied July database (3 min)
- [ ] Mark each customer column: direct identifier, indirect identifier or neither (8 min)
- [ ] Label each table with a classification level and a reason (6 min)
- [ ] Write the analyst view with only the columns the purpose needs (10 min)
- [ ] Run the analysts' three questions on the view and test that the identifiers are absent (8 min)
- [ ] ✱ Stretch: Write a second view for the delivery team and list what it needs that the analysts do not

### Session 3: Query plans and indexes

#### [day4#s3] Query plans and indexes

*Session 3*

- Read the operators of a query plan from the bottom up
- Find where a filter is applied in a plan
- Predict when an index changes a plan and when it does not

#### [day4#explain] A plan is a tree of operators: read it from the bottom up

*EXPLAIN*

1. **Seq Scan** returns, filter on the date · reasons
2. **Hash Join** on reason_code
3. **Hash Group By** by label, sum of refund
4. **Projection** the columns returned

```sql
-- file: returns desk
EXPLAIN
SELECT r.label, SUM(t.refund)
FROM returns t JOIN reasons r ON r.reason_code = t.reason_code
WHERE t.received_on >= DATE '2026-05-03'
GROUP BY r.label;
```

#### [day4#filter-in-plan] The engine applies a filter as early as it can, often inside the scan

*Where the filter is*

- In the returns plan, the date condition appears in the **scan** of returns, under `Filters:`
- Rows that fail it never reach the join: less to match, less to group
- The numbers after `~` are the engine's **estimates**, made before running, not counts
- A filter on the result of a group (HAVING) cannot move down: it needs the groups first

> **What goes wrong.** Reading the estimates as row counts. To count, run the query; to see the shape, read the plan.

#### [day4#scan-search] An index lets a lookup go straight to its rows instead of reading them all

*Indexes*

```sql
-- file: returns desk, SQLite
EXPLAIN QUERY PLAN
SELECT * FROM returns
WHERE order_ref = 'O-A15';
-- SCAN returns

CREATE INDEX ix_returns_order
  ON returns (order_ref);
-- the same lookup:
-- SEARCH returns USING INDEX
--   ix_returns_order (order_ref=?)
```

- **SCAN**: every row is read and tested
- **SEARCH**: the index leads to the matching rows
- A total over the whole table stays a **SCAN** with or without the index

SQLite, from Python's standard library (`_tools/slide_examples.py`, index-scan-search). No timings: the plan's shape is what is stable.

#### [day4#when-index] An index helps a query that picks few rows by the indexed column

*When it helps*

| Query on returns, index on order_ref | Plan | Why |
| --- | --- | --- |
| `WHERE order_ref = 'O-A15'` | search | an exact value of the indexed column |
| `SUM(refund)` over all returns | scan | every row is needed anyway |
| `WHERE order_ref LIKE '%15'` | scan | a pattern starting with % has no place to jump to |
| `WHERE reason_code = 'R1'` | scan | not the indexed column |

> **Takeaway.** Analytical queries read most of a table, so they rarely gain from an index. Lookups do.

#### [day4#check-index] Which query can an index on patient_id turn into a search?

*Checkpoint*

**Question:** A clinic's appointments table, 2 million rows, an index on patient_id.

- A. appointments per month this year
- B. appointments of doctor D12
- C. patients whose number ends in 42
- D. appointments of patient P-1093

#### [day4#lab-4-3] Read two plans and watch an index change one

Lab 4.3 · 30 min

Read a join plan in DuckDB, then watch an index turn a scan into a search in SQLite; plan shapes only, no timings

[D4_3_plans_and_indexes.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_3_plans_and_indexes.ipynb)

- [ ] Read the plan of a join and group query (8 min)
- [ ] Find where the filter is applied (5 min)
- [ ] Read the plan of a lookup in the second engine before an index (5 min)
- [ ] Create the index and read the new plan (6 min)
- [ ] Write when an index helps an analytical query and when it does not (6 min)
- [ ] ✱ Stretch: Create a two-column index and find which order of the columns the lookup can use

### Session 4: Testing queries against known answers

#### [day4#s4] Testing queries against known answers

*Session 4*

- Build a small fixture and work out the expected answer by hand
- Write a test that compares a query's result with the expected rows
- Classify a failing generated query: fan-out, wrong grain or a missing business rule

#### [day4#known-answers] A query is right when it matches an answer worked out by hand

*Testing*

1. **1 · Fixture** tables small enough to print
2. **2 · Expected** the answer on paper, from the rule
3. **3 · Run** the query on the fixture
4. **4 · Compare** pass, or find out why

> **Takeaway.** The expected answer must not come from SQL: another query can share the mistake.

#### [day4#three-failures] Most wrong totals are one of three mistakes

*Why queries fail*

- **Fan-out.** A join repeats rows. Returns joined to inspections: T2's refund counted twice.
- **Wrong grain.** The right sum at the wrong level: an average per item when the question is per return.
- **Missing rule.** Well formed, but a business rule is left out: the desk's rule says a return with no refund counts as 0.

#### [day4#test-example] The average refund per return: the generated query against the rule

*A test that fails*

- **17.44** `AVG(refund)`: skips T4, whose refund is empty
- **13.95** by hand, with T4 as 0: 69.75 over 5 returns

Test: FAIL. Kind: **missing rule**. The fix is one `COALESCE`; finding it took the rule and a fixture.

The returns desk (`_tools/slide_examples.py`, test-avg-refund).

#### [day4#verification-note] Every generated query ships with its test and a judgement

*The verification note*

| Query | Expected | Got | Test · judgement |
| --- | --- | --- | --- |
| avg_refund | 13.95 | 17.44 | FAIL · missing rule |
| returns_r2 | 2 | 2 | pass · ok |

- Generated SQL is a **draft** until it passes a test against answers someone checked by hand
- The capstone asks for the same: a test per question and a log of any generated SQL and how it was checked

#### [day4#check-test] A generated query passes its test. What does that show?

*Checkpoint*

**Question:** A pharmacy fixture has six orders, none with two delivery attempts. The generated revenue query matches the hand-checked answer.

- A. The query is correct on the full data
- B. It follows the rule on the cases the fixture holds; repeat attempts are untested
- C. Nothing: generated queries cannot be trusted
- D. The fixture is too small to mean anything

#### [day4#lab-4-4] Ten generated queries against hand-checked answers

Lab 4.4 · 35 min

Hand-check the answers of ten questions on the mini tables, run ten supplied generated-style queries through tests against them, classify each failure against the revenue rule and write the verification note

[D4_4_ten_generated_queries.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D4_4_ten_generated_queries.ipynb)

- [ ] Read the revenue rule and the ten questions (5 min)
- [ ] Work out the expected answers on the mini tables by hand (10 min)
- [ ] Run the ten queries through the tests (8 min)
- [ ] Classify each failure: fan-out, grain or a missing rule (7 min)
- [ ] Write the verification note with each test result (5 min)
- [ ] ✱ Stretch: Ask an approved assistant for the same ten questions, given only the schema, and run its queries through the same tests

#### [day4#wrap-up] Three things to keep from Day 4

*Wrap-up*

- **Refuse and account.** Constraints refuse bad rows; the log accounts for every row read.
- **Expose the minimum.** A view per purpose, tested; Restricted rows stay out of assistants.
- **Prove it by hand.** A query is right when it matches an answer worked out on a fixture.

#### [day4#next] Capstone: the business orders brief

*Next*

- Tonight and before the capstone day: the brief in `labs/capstone/`, ten questions, a test per question
- On the day: the timed check with the assistant off, then five minutes adapting one of your queries live
