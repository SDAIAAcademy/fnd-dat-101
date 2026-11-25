---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/slides/day1.html"
---

# SQL and Relational Data

## Day 1: Tables, keys and grain

What a row means before any query is written

#### [day1#title] Tables, keys and grain

*SDAIA Academy · SQL and Relational Data*

Day 1: What a row means before any query is written

Data & AI Foundations Track · 4 teaching days + capstone day · 4 sessions · 4 labs · FND-DAT-101

#### [day1#agenda] Tables, keys and grain

*Today*

- **Session 1 · Tables, types, keys and constraints**: A table is a set of rows of one kind; keys name a row, constraints refuse a bad one
- **Session 2 · Grain and cardinality**: What one row stands for, and how many rows of one table meet one row of another
- **Session 3 · Normal forms, wide tables and embedded engines**: Why operational tables are split, why analytical tables are wide, and where the engine runs
- **Session 4 · Filters, sorting and expressions**: WHERE on text and dates, ORDER BY with ties, and expressions that compute a value per row

#### [day1#setup-check] One notebook proves your setup works

*Before the first session*

Open `labs/00_setup_check.ipynb` in Colab or on your laptop and run every cell. It writes the company's six tables, builds the database file and runs one query.

- It ends with **setup ok** and the six table names
- The first run takes about half a minute; later runs reuse the file
- No model, no key and no account is needed for any lab

- **On a laptop.** From the `labs` folder: `uv run --with jupyterlab jupyter lab`, then open the notebook. In Colab the first cell clones the course and installs the two packages.

### Session 1: Tables, types, keys and constraints

#### [day1#s1] Tables, types, keys and constraints

*Session 1*

- Name the type and the role of each column of a table
- Test a candidate key with a counting query
- Read the message a database gives when a constraint refuses a row

#### [day1#table-holds-one-kind] A table holds rows of one kind, each with the same columns

*What a table is*

| return_id | order_ref | reason_code | refund | received_on |
| --- | --- | --- | --- | --- |
| T1 | O-A11 | R1 | 12.00 | 2026-05-02 |
| T2 | O-A12 | R2 | 30.50 | 2026-05-02 |
| T3 | O-A15 | R1 | 8.25 | 2026-05-03 |
| T4 | O-A15 | R3 | NULL | 2026-05-04 |
| T5 | O-A20 | R2 | 19.00 | 2026-05-06 |

The company's returns desk: the `returns` table. The slides use this department; the labs use the delivery tables.

> **Unlike a sheet.** No merged cells, no totals row, no colour that means something. Every fact sits in a column with a name.

#### [day1#types-decide-what-fits] Every column has a type, and the type decides what fits

*Types*

| Type | Holds | Example |
| --- | --- | --- |
| `VARCHAR` | text | `'R1'` |
| `INTEGER` | whole numbers | `3` |
| `DECIMAL(8,2)` | exact amounts, two decimals | `30.50` |
| `DATE`, `TIMESTAMP` | a day; a day and a time of day | `DATE '2026-05-02'` |
| `BOOLEAN` | true or false | `true` |

> **What goes wrong.** An amount stored as text sorts as text: `'9.00'` comes after `'30.50'`. A date stored as text cannot be compared with a range.

#### [day1#key-names-one-row] A key is a column, or a set of columns, that names exactly one row

*Keys*

- **A single-column key.** `return_id` in `returns`: no two returns share it. Declared as `PRIMARY KEY`, the engine refuses a second T3.
- **A composite key.** `(return_id, item_no)` in `return_items`: a return has several items, so the return alone does not name an item; the pair does.

> **Not a key.** `order_ref` looks like an identifier, but one order can be returned twice: O-A15 appears in T3 and T4.

#### [day1#key-by-counting] Test a candidate key by counting rows and distinct values

*Proof, not belief*

```sql
-- file: returns desk
SELECT COUNT(*)                  AS n_rows,
       COUNT(DISTINCT order_ref) AS n_refs
FROM returns;
-- n_rows 5, n_refs 4
```

- Equal numbers: no value repeats, **the candidate holds**
- Fewer distinct values: some value repeats, **not a key**
- For a pair, count the rows of `SELECT DISTINCT a, b`: 8 pairs for 8 rows of `return_items`

> **Habit.** Before you trust a key, count. It takes one query.

#### [day1#foreign-key-points] A foreign key points at a row that must exist in another table

*Between tables*

**return_items** `return_id` T5 → **returns** row T5 must exist → **reasons** its `reason_code` R2 must exist

Declared with `REFERENCES returns (return_id)`, an item for a return that does not exist is refused. Without it, the item would sit in the table, joined to nothing, and every total would quietly miss it.

#### [day1#constraints-refuse] Constraints refuse rows that make no sense, before anyone queries them

*Constraints*

- **NOT NULL.** The value must be there: every return has a received date.
- **PRIMARY KEY, UNIQUE.** No two rows share the value.
- **REFERENCES.** The value exists in the other table.
- **CHECK.** A rule on the value: `qty > 0`, `refund >= 0`.
- **Type.** Only that kind of value: no text in a date.
- **The message.** A refusal names the rule it broke. Read it.

#### [day1#six-tables] The grocery delivery company keeps its orders in six tables

*The case study*

- **stores.** Eight dispatch stores across five regions
- **products.** The catalogue: names, categories, list prices
- **customers.** Registered customers, with personal data
- **orders.** Placed by a customer at a store, with a status
- **order_lines.** Products, quantities, prices, discounts
- **deliveries.** What happened when a courier went out

Synthetic: January to June 2026, about a million order lines. People appear only as codes and roles.

#### [day1#check-key] Which column is a key of return_items?

*Checkpoint*

**Question:** The returns desk's `return_items` has 8 rows. `COUNT(DISTINCT return_id)` is 5 and `COUNT(DISTINCT product_ref)` is 5. The distinct pairs `(return_id, item_no)` number 8. What names one row?

- A. return_id alone
- B. The pair return_id and item_no
- C. product_ref alone
- D. No column: the table has no key

#### [day1#lab-1-1] Six tables and their keys

Lab 1.1 · 35 min

List the six tables of the grocery delivery company, read their columns and types, test each candidate key by counting, and watch a key and a check refuse bad rows

[D1_1_tables_and_keys.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_1_tables_and_keys.ipynb)

- [ ] List the six tables with their row counts (5 min)
- [ ] Describe the columns and types of each table (7 min)
- [ ] Test each candidate key: COUNT(\*) against COUNT(DISTINCT key) (10 min)
- [ ] Break a key and a check on the mini tables and read the refusals (8 min)
- [ ] Write down what each table refuses and why (5 min)
- [ ] ✱ Stretch: Find one column whose type is weaker than its meaning and say what that lets in

### Session 2: Grain and cardinality

#### [day1#s2] Grain and cardinality

*Session 2*

- State the grain of a table in one sentence
- Confirm a grain with a counting query
- Measure a one-to-many relationship and name its maximum

#### [day1#grain-one-row] The grain is what one row stands for

*Grain*

- **returns.** One row per **returned parcel**
- **return_items.** One row per **item inside one return**
- **inspections.** One row per **inspection of one return**; a return can be inspected twice

> **Say it in one sentence.** "One row per ..." If you cannot finish the sentence, you cannot sum the table safely.

#### [day1#grain-sentences] A good grain sentence names the thing and the one it belongs to

*Writing it down*

| Vague | Precise |
| --- | --- |
| "Items" | One row per item inside one return |
| "Inspection data" | One row per inspection of one return, on one day |
| "Refunds by reason" | One row per reason code, with the sum of refunds |

The precise sentence tells you the key: the thing, plus whatever tells two of them apart.

#### [day1#cardinality-kinds] Cardinality says how many rows of one table meet one row of another

*Cardinality*

- **One to one.** Each return has exactly one decision letter.
- **One to many.** Each return has one or more items.
- **Many to many.** Products and returns: resolved through `return_items`.

> **Write it as a range.** "Items per return: 1..3" says more than "one to many": it gives the fewest and the most.

#### [day1#measure-cardinality] Group the many side by the key of the one side, then read the smallest and largest group

*Measure it*

```sql
-- file: returns desk
SELECT MIN(n) AS fewest, MAX(n) AS most
FROM (SELECT return_id, COUNT(*) AS n
      FROM return_items
      GROUP BY return_id);
-- fewest 1, most 3
```

> **What goes wrong.** This query only sees returns that have items. A return with no item would not appear in the inner result, so "fewest" can never read 0 here.

#### [day1#fewest-is-the-trap] To see the zeros, count from the one side

*The zero case*

```sql
-- file: returns desk
SELECT r.reason_code,
       COUNT(t.return_id) AS returns
FROM reasons r
LEFT JOIN returns t
  ON t.reason_code = r.reason_code
GROUP BY r.reason_code;
```

| reason_code | returns |
| --- | --- |
| R1 | 2 |
| R2 | 2 |
| R3 | 1 |
| R4 | 0 |

Reasons to returns: **0..2**. Grouping `returns` alone would have said 1..2 and hidden R4.

#### [day1#join-takes-finest-grain] A join takes the grain of its finest table

*Looking ahead*

1. **returns** 5 rows, one per return
2. **join inspections** a return inspected twice appears twice
3. **sum of refunds** counts that refund twice

> **Keep for Day 3.** Before every join, write the grain of each side. If the result's grain is finer than the question's, aggregate first.

#### [day1#check-grain] What is the grain of the inspections table?

*Checkpoint*

**Question:** The returns desk inspects some returns once, some twice, and some never. `inspections` holds `return_id`, `inspected_on` and `result`. Which sentence states its grain?

- A. One row per return
- B. One row per inspection result
- C. One row per return, inspected or not
- D. One row per inspection of one return

#### [day1#lab-1-2] The annotated schema

Lab 1.2 · 35 min

Write the key and the grain of each of the six tables, confirm them with counting queries, measure the cardinality of every relationship and check the annotated schema against the reference

[D1_2_annotated_schema.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_2_annotated_schema.ipynb)

- [ ] Write the grain of each table in one sentence (6 min)
- [ ] Confirm each grain with a counting query (10 min)
- [ ] Measure lines per order, attempts per order and orders per customer (10 min)
- [ ] Fill in the annotated schema and run its check (9 min)
- [ ] ✱ Stretch: List every join of the schema that can multiply rows, and the column that causes it

### Session 3: Normal forms, wide tables and embedded engines

#### [day1#s3] Normal forms, wide tables and embedded engines

*Session 3*

- Explain the repetition that normal forms remove
- Build a wide analytical table from a join and name its risks
- Contrast an embedded engine with a client-server database

#### [day1#normal-forms-brief] Normalised tables store each fact once

*Normal forms, in brief*

| Form | The rule, in plain words | Returns desk example |
| --- | --- | --- |
| First | One value per cell; no lists inside a cell | Items in their own rows, not "X-101, X-205" in one cell |
| Second | Every column depends on the whole key | The reason label is not in `return_items`: it depends on the return, not the item |
| Third | No column depends on another non-key column | The label lives in `reasons`, reached through `reason_code` |

#### [day1#update-anomaly] A fact written many times can disagree with itself

*Why it matters*

- **Reason label copied onto every item.** Rename R2 from "wrong item" to "wrong product". Change 3 of the 5 rows that carry it and the table now holds both labels for the same code.
- **Label stored once in reasons.** Change one row. Every query that joins to `reasons` sees the new label at once.

> **The update anomaly.** It needs no bug: only a partial fix, which is what busy people make.

#### [day1#analytical-tables-wide] Analytical tables are wide on purpose

*The other side*

- **Read far more than written**: an analysis reads millions of rows and changes none
- **Fewer joins** for every question: the category and region already sit on the line
- **Built from the normalised source** on a schedule, never edited by hand
- Columnar engines store each column apart, so **unused wide columns cost little** to read

> **The rule.** A wide table is a copy. When it is wrong, fix the source and rebuild the copy.

#### [day1#embedded-vs-server] An embedded engine runs inside your program; a server runs apart and you connect to it

*Where the engine runs*

- **Embedded.**
  - A library in your Python process
  - The database is a file
  - Nothing to install or administer
  - One writer at a time, on one machine
- **Client-server.**
  - A separate server process, often another machine
  - Accounts, permissions, network
  - Many users reading and writing at once
  - Someone runs and backs it up

The SQL you learn here runs on both, with small differences of dialect.

#### [day1#two-embedded-engines] Two embedded engines, built for different work

*The tool slot*

|  | Analytical engine (DuckDB) | Transactional engine (SQLite) |
| --- | --- | --- |
| Built for | Scans and aggregates over many rows | Many small reads and writes |
| Stores | Column by column, processed in batches | Row by row |
| In this course | Every lab on the full data | Lab 1.3 on the mini tables; lab 4.3 for indexes |

Examples of a capability, not endorsements. Either engine is free and runs on a laptop processor.

#### [day1#check-wide] The wide returns table shows two labels for R2. What do you do?

*Checkpoint*

**Question:** The returns desk's wide table copies the reason label onto every item. A colleague renamed R2 in some rows only, so both labels now appear. What is the right fix?

- A. Correct the label once in reasons and rebuild the wide table
- B. Update the remaining rows of the wide table
- C. Add DISTINCT to every report on the wide table
- D. Delete the reasons table and keep the wide one

#### [day1#lab-1-3] One wide table, and what it repeats

Lab 1.3 · 30 min

Join order lines to their order, store and product into one wide table, count what it repeats, make one copy disagree, and run the same count in a second embedded engine

[D1_3_wide_table.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_3_wide_table.ipynb)

- [ ] Build a wide table of order lines with store and product columns (8 min)
- [ ] Count how often each store's region is repeated (6 min)
- [ ] Change one region in the wide table and find the rows that now disagree (8 min)
- [ ] Run the same count in the second embedded engine (8 min)
- [ ] ✱ Stretch: Write two sentences on when the wide table is the right choice and who must rebuild it

### Session 4: Filters, sorting and expressions

#### [day1#s4] Filters, sorting and expressions

*Session 4*

- Filter rows on text patterns and date ranges
- Sort with a tie-breaker and keep the top rows
- Compute a value per row with an expression that handles a NULL

#### [day1#logical-order] You write SELECT first, but the engine reads FROM first

*How a query is read*

1. **1 · FROM** which table
2. **2 · WHERE** which rows
3. **3 · SELECT** which columns, computed how
4. **4 · ORDER BY, LIMIT** in which order, how many

> **Read in this order** when you predict a result: start with the table, then cross out rows, then pick columns.

#### [day1#where-keeps-true] WHERE keeps the rows for which the condition is true

*Filters*

```sql
-- file: returns desk
SELECT return_id, refund
FROM returns
WHERE reason_code = 'R1'
  AND refund >= 10;
-- T1 12.00
```

- Comparisons: `=`, `<>`, `<`, `>=`
- Combine with `AND`, `OR`, `NOT`; use brackets when you mix them
- A list: `reason_code IN ('R1', 'R2')`
- Text is in single quotes; column names are not

#### [day1#text-patterns] = matches exactly; LIKE and ILIKE match a pattern

*Text*

| Condition | Keeps |
| --- | --- |
| `product_ref = 'X-101'` | exactly that code |
| `product_ref LIKE 'X-1%'` | codes starting with X-1; `%` is any run of characters |
| `label ILIKE '%item%'` | "item" anywhere, in any letter case |
| `LOWER(label) = 'late'` | "late", "Late", "LATE" |

> **What goes wrong.** In DuckDB `LIKE` is case-sensitive: `LIKE '%Item%'` misses "wrong item". SQLite ignores case for plain letters: the same query behaves differently in another engine.

#### [day1#half-open-dates] Filter a period with a half-open range: from the first day, up to but not including the next

*Dates and times*

```sql
-- file: returns desk
SELECT COUNT(*)
FROM returns
WHERE received_on >= DATE '2026-05-02'
  AND received_on <  DATE '2026-05-04';
-- 3 returns: T1, T2, T3
```

> **What goes wrong.** On a timestamp column, `BETWEEN '2026-05-02' AND '2026-05-03'` stops at the first instant of 3 May and drops the rest of that day.

#### [day1#order-needs-tiebreak] ORDER BY needs a tie-breaker before LIMIT can be trusted

*Sorting*

```sql
-- file: returns desk
SELECT return_id, received_on
FROM returns
ORDER BY received_on DESC,
         return_id
LIMIT 2;
-- T5 2026-05-06
-- T4 2026-05-04
```

- `DESC` from the highest; ascending is the default
- T1 and T2 share a date: without `return_id` their order is not defined
- `LIMIT n` keeps the first n rows after sorting

#### [day1#expressions] An expression computes a new value for each row

*Expressions*

```sql
-- file: returns desk
SELECT return_id,
       COALESCE(refund, 0) AS refund_or_zero,
       date_trunc('month', received_on) AS month,
       UPPER(reason_code) AS code
FROM returns;
```

- Arithmetic: `qty * price`
- `COALESCE(x, 0)`: x, or 0 when x is NULL; T4 shows 0.00
- `date_trunc('month', d)`: the first day of d's month
- `AS name` names the new column

> **What goes wrong.** `refund - 1` on T4 is NULL, not -1: anything combined with NULL is NULL.

#### [day1#predict-first] Write your prediction before you run the query

*The habit of the course*

- **How many rows?** One, a handful, about a sixth of the table
- **Roughly what value?** An order of magnitude, a sign, a range
- **Which first row?** After the sort you asked for

> **Why.** A result that surprises you is either a discovery or a bug. Without a prediction you cannot tell that you were surprised.

#### [day1#check-dates] Which filter counts every inspection made in May 2026?

*Checkpoint*

**Question:** The returns desk stores `inspected_at` as a TIMESTAMP. You need every inspection of May 2026, including those late on 31 May.

- A. inspected_at BETWEEN '2026-05-01' AND '2026-05-31'
- B. inspected_at LIKE '2026-05%'
- C. inspected_at >= '2026-05-01' AND inspected_at < '2026-06-01'
- D. inspected_at >= '2026-05-01' AND inspected_at <= '2026-06-01'

#### [day1#lab-1-4] Questions 1 to 4, predicted first

Lab 1.4 · 35 min

Write a prediction, then the query, for the first four of the twenty business questions: text filters, a date range, a sorted top ten and a line value; save them to your answer file

[D1_4_questions_1_to_4.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D1_4_questions_1_to_4.ipynb)

- [ ] Read the four questions and write a prediction for each (5 min)
- [ ] Answer questions 1 and 2: a text filter and a date range (12 min)
- [ ] Answer questions 3 and 4: a sorted top ten and a line value (12 min)
- [ ] Compare each result with your prediction and save the part file (6 min)
- [ ] ✱ Stretch: Rewrite question 2 with a half-open date range and explain why it is safer than BETWEEN

#### [day1#wrap-up] Three things to keep from Day 1

*Wrap-up*

- **Count, then trust.** A key is proven by COUNT(\*) against COUNT(DISTINCT).
- **Say the grain.** "One row per ..." before every sum and every join.
- **Predict first.** Rows, value or first row, written before you run.

#### [day1#next] Day 2: one table, then two

*Next*

- Finish the annotated schema and questions 1 to 4 if you did not: about 30 minutes
- Keep `answers/part1.sql`: the checker reads it on Day 3
- Tomorrow: CASE, NULL, groups and the four kinds of join
