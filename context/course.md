---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/"
---

# SQL and Relational Data

Query relational data in SQL, predict the result before you run it, and prove the answer right against a known one

Participants query relational data in SQL and check that the answers are right. In an embedded analytical engine on a laptop they move from keys and constraints through joins, grouping and common table expressions to window functions. They predict results before running queries, catch the silent errors that joins and NULLs cause, and test assistant-written SQL against known answers. The capstone answers a stakeholder brief on an unseen dataset.

- **Audience:** Beginners. Anyone starting technical data or AI work, including future analysts, data scientists, data engineers and AI engineers who can code but have not yet worked with messy real data.
- **Prerequisites:** Comfortable with spreadsheets: filters, sorting and simple formulas; No programming experience required
- **Case study:** The grocery delivery company: An online grocery and household goods delivery business in one city of five regions, dispatching from eight stores; every lab works on its synthetic six-table schema of about a million order lines from January to June 2026, with planted traps: delivery attempts that multiply rows, discounts left NULL, cancelled lines, closed days and a revenue rule finance keeps outside the schema. The capstone uses an unseen dataset from the company's business orders service; all data is synthetic and people appear only as roles and codes.

## Outcomes

- LO1 (Awareness): Explain the relational model: tables, keys, constraints, NULL and the grain of a table, given a six-table synthetic delivery schema
- LO2 (Awareness): Identify the output of joins, grouping and NULL comparisons before running them, given small printed tables
- LO3 (Applied): Write queries with filters, joins, grouping, subqueries and common table expressions that answer business questions, given a synthetic dataset of about a million order lines
- LO4 (Applied): Apply window functions to rank rows, compare periods and compute running and moving totals, given daily order tables
- LO5 (Applied): Implement a small schema with keys and constraints, load raw files into it and report rejected rows, given extracts with seeded defects
- LO6 (Awareness): Identify silent errors in assistant-written SQL, such as join fan-out, wrong grain and missing business rules, given ten generated queries and a revenue rule documented outside the schema

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

## Day 2: One table, then two

Conditions, NULL, groups and the four kinds of join

#### [day2#title] One table, then two

*SDAIA Academy · SQL and Relational Data*

Day 2: Conditions, NULL, groups and the four kinds of join

Data & AI Foundations Track · 4 teaching days + capstone day · 4 sessions · 4 labs · FND-DAT-101

#### [day2#agenda] One table, then two

*Today*

- **Session 1 · CASE expressions and set operations**: CASE turns rules into columns; UNION, INTERSECT and EXCEPT combine whole result sets
- **Session 2 · NULL and three-valued logic**: NULL is unknown, not zero or empty: comparisons with it are neither true nor false
- **Session 3 · Grouping and having**: GROUP BY changes the grain of the result; HAVING filters groups after they are formed
- **Session 4 · Inner, outer, semi and anti joins**: Which rows survive a join, and how to ask for rows that have, or lack, a partner

#### [day2#review-day1] Which statement about the returns desk's tables is right?

*Review of Day 1*

**Question:** `returns` has 5 rows and 4 distinct `order_ref` values; `inspections` can hold two rows for one return.

- A. order_ref is a key of returns
- B. The grain of inspections is one row per return
- C. Joining returns to inspections can repeat a return
- D. A join to inspections keeps exactly 5 rows

### Session 1: CASE expressions and set operations

#### [day2#s1] CASE expressions and set operations

*Session 1*

- Write a CASE expression that sorts rows into bands
- Count by condition with CASE inside an aggregate
- Combine two result sets with UNION, INTERSECT or EXCEPT

#### [day2#case-turns-rules] CASE turns a rule into a column

*CASE*

```sql
-- file: returns desk
SELECT return_id, item_no, qty,
  CASE WHEN qty = 1  THEN 'single'
       WHEN qty <= 3 THEN 'few'
       ELSE 'many'
  END AS band
FROM return_items;
```

- Branches are tried **in order**; the first true one wins
- `ELSE` catches the rest; without it, the rest is NULL
- Every branch returns the same type

> **What goes wrong.** Put `qty <= 3` first and a quantity of 1 becomes "few".

#### [day2#case-in-aggregate] A CASE inside SUM counts the rows that meet a condition

*Counting by condition*

```sql
-- file: returns desk
SELECT reason_code,
       SUM(CASE WHEN refund >= 15 THEN 1 ELSE 0 END) AS large,
       COUNT(*) FILTER (WHERE refund < 15)            AS small
FROM returns
GROUP BY reason_code;
```

- Two counts side by side, from one pass over the table
- `FILTER (WHERE ...)` says the same thing more briefly where the engine supports it
- A refund that is NULL is neither large nor small: count it on purpose if it matters

#### [day2#set-operations] UNION, INTERSECT and EXCEPT combine whole result sets

*Set operations*

- **UNION.** In either set, duplicates removed. `UNION ALL` keeps them.
- **INTERSECT.** In both sets.
- **EXCEPT.** In the first set and not in the second.

```sql
-- file: returns desk
SELECT product_ref FROM return_items WHERE return_id IN ('T1', 'T2')
INTERSECT
SELECT product_ref FROM return_items WHERE return_id = 'T5';
-- X-101, X-205: products returned in both groups
```

#### [day2#sets-compare-rows] Set operations compare whole rows, so choose the columns first

*The catch*

- **Too many columns.** `SELECT *` on both sides: two different returns never match, so `EXCEPT` takes nothing away.
- **The column the question is about.** `SELECT product_ref` on both sides: the comparison is between products, as asked.

> **Habit.** Say "a set of what?" before writing either side.

#### [day2#union-all] UNION removes duplicates; UNION ALL keeps every row

*UNION or UNION ALL*

| You want | Use |
| --- | --- |
| A list of distinct products returned in May or June | `UNION` |
| All return items of May and June, to sum quantities | `UNION ALL`: duplicates are real items |

> **What goes wrong.** `UNION` under a sum silently merges two identical items of different returns, and the total shrinks.

#### [day2#check-case] Which query lists products returned in May but not in June?

*Checkpoint*

**Question:** The returns desk wants the distinct product codes returned in May 2026 that were not returned in June 2026.

- A. May's product codes EXCEPT June's product codes
- B. May's item rows EXCEPT June's item rows
- C. May's product codes UNION June's product codes
- D. May's product codes INTERSECT June's product codes

#### [day2#lab-2-1] Questions 5 to 7: bands and sets

Lab 2.1 · 30 min

Predict, then answer three business questions with CASE bands, conditional counts and a set operation; save them to your answer file

[D2_1_questions_5_to_7.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_1_questions_5_to_7.ipynb)

- [ ] Write a prediction for each of the three questions (4 min)
- [ ] Question 5: order lines in quantity bands (8 min)
- [ ] Question 6: paid and free delivery per order status (8 min)
- [ ] Question 7: January customers who did not order in June (7 min)
- [ ] Save the part file (3 min)
- [ ] ✱ Stretch: Answer question 7 again with NOT EXISTS and confirm both give the same count

### Session 2: NULL and three-valued logic

#### [day2#s2] NULL and three-valued logic

*Session 2*

- Predict the rows a comparison with NULL keeps
- Use IS NULL, COALESCE and IS DISTINCT FROM on purpose
- Explain why NOT IN with a NULL returns no rows

#### [day2#null-is-unknown] NULL means unknown: not zero, not empty text, not false

*NULL*

- **Unknown.** T4's refund has not been decided.
- **Not applicable.** A line with no discount, in some designs.
- **Not recorded.** A customer who gave no region.

> **One marker, several meanings.** The schema rarely says which. The business rule does: the finance rule of this course says an empty discount means none.

#### [day2#three-valued] A comparison with NULL is neither true nor false: it is unknown

*Three-valued logic*

| Condition on T4 (refund NULL) | Result | Kept by WHERE? |
| --- | --- | --- |
| `refund = 12.00` | unknown | no |
| `refund <> 12.00` | unknown | no |
| `refund = NULL` | unknown | no |
| `refund IS NULL` | true | yes |

WHERE keeps a row only when its condition is true.

#### [day2#and-or-unknown] AND, OR and NOT carry the unknown through

*Combining unknowns*

- **AND.** false AND unknown = **false**
  true AND unknown = **unknown**
- **OR.** true OR unknown = **true**
  false OR unknown = **unknown**
- **NOT.** NOT unknown = **unknown**

> **What goes wrong.** `NOT (refund = 12.00)` does not bring T4 back: the NOT of unknown is still unknown.

#### [day2#null-tools] Three tools make NULL behave the way the question needs

*Saying what you mean*

| Tool | Use it when |
| --- | --- |
| `x IS NULL`, `x IS NOT NULL` | you ask whether a value is missing |
| `COALESCE(x, 0)` | a missing value means a known default |
| `x IS DISTINCT FROM y` | you want "different", with NULL treated as a value |

```sql
-- file: returns desk
SELECT COUNT(*) FROM returns WHERE refund IS DISTINCT FROM 12.00;  -- 4: T4 included
```

#### [day2#not-in-trap] NOT IN with a NULL in the list keeps no row at all

*The classic trap*

1. **Written** `code NOT IN ('R1', NULL)`
2. **Means** `code <> 'R1' AND code <> NULL`
3. **Becomes** something AND unknown: never true

> **Use NOT EXISTS** when the list comes from a subquery that might contain a NULL.

#### [day2#null-in-aggregates] Aggregates skip NULLs, except COUNT(\*)

*Aggregates*

- **5** COUNT(\*)
- **4** COUNT(refund)
- **69.75** SUM(refund)
- **17.44** AVG(refund)

AVG divides 69.75 by the 4 known refunds. If an unknown refund should count as 0, the question wants `AVG(COALESCE(refund, 0))` = 13.95.

The returns desk, 5 returns, one refund NULL (`_tools/slide_examples.py`).

#### [day2#check-null] How many inspections does this query count?

*Checkpoint*

**Question:** An inspections table has 6 rows. `result` is 'pass' in 3, 'fail' in 1 and NULL in 2. What does `SELECT COUNT(*) FROM inspections WHERE result <> 'pass'` return?

- A. 3
- B. 6
- C. 0
- D. 1

#### [day2#lab-2-2] Predict, then run: twelve NULL comparisons

Lab 2.2 · 35 min

With the assistant off, predict the row count of twelve short queries on the printed mini tables, run them, mark each prediction and repair the ones that did not say what was meant

[D2_2_null_predictions.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_2_null_predictions.ipynb)

- [ ] Print the mini customers and order lines (3 min)
- [ ] Predict the row count of each of the twelve queries on paper (12 min)
- [ ] Run the twelve and mark each prediction (8 min)
- [ ] Rewrite three queries so they say what was meant (9 min)
- [ ] Write the NULL rule you will keep (3 min)
- [ ] ✱ Stretch: Show NOT IN returning no rows when the list holds a NULL, and the NOT EXISTS that does not

### Session 3: Grouping and having

#### [day2#s3] Grouping and having

*Session 3*

- Predict the number of rows a GROUP BY returns
- Choose between WHERE and HAVING for a condition
- Count distinct values inside a group

#### [day2#group-changes-grain] GROUP BY changes the grain: one row per group

*GROUP BY*

```sql
-- file: returns desk
SELECT reason_code,
       COUNT(*)    AS returns,
       SUM(refund) AS refunds
FROM returns
GROUP BY reason_code;
```

| reason_code | returns | refunds |
| --- | --- | --- |
| R1 | 2 | 20.25 |
| R2 | 2 | 49.50 |
| R3 | 1 | NULL |

Five rows in, three out: **one row per reason that occurs**. R4 has no return, so no group.

#### [day2#select-what-groups] After GROUP BY, SELECT may show only group columns and aggregates

*The rule*

- **Refused, or meaningless.** `SELECT reason_code, return_id, COUNT(*) ... GROUP BY reason_code`: which of R1's two returns would the row show?
- **Fine.** `SELECT reason_code, COUNT(*), MAX(received_on) ... GROUP BY reason_code`

> **Read it as** "for each reason code, tell me ...". Anything else needs an aggregate.

#### [day2#where-vs-having] WHERE filters rows before grouping; HAVING filters groups after

*WHERE or HAVING*

1. **FROM** returns
2. **WHERE** refund IS NOT NULL
3. **GROUP BY** reason_code
4. **HAVING** COUNT(\*) >= 2
5. **SELECT, ORDER BY**

Without the WHERE, the reasons with at least two returns are R1 and R2. A condition on a single row's value goes in WHERE; a condition on a count or a sum goes in HAVING.

#### [day2#count-distinct] COUNT(DISTINCT x) counts different values inside each group

*Counting things, not rows*

| Expression | Counts | Returns desk, all items |
| --- | --- | --- |
| `COUNT(*)` | rows | 8 |
| `COUNT(DISTINCT return_id)` | different returns | 5 |
| `COUNT(DISTINCT product_ref)` | different products | 5 |

> **What goes wrong.** "How many customers ordered in May" with `COUNT(*)` counts orders.

#### [day2#group-by-expression] Group by an expression to get one row per month, week or band

*Groups of time*

```sql
-- file: returns desk
SELECT CAST(date_trunc('week', received_on) AS DATE) AS week,
       COUNT(*) AS returns
FROM returns
GROUP BY week
ORDER BY week;
```

- The expression in SELECT and in GROUP BY must be the same; the alias saves retyping it
- In DuckDB `date_trunc` returns a timestamp, even on a `DATE`: cast it to `DATE` for a clean label

#### [day2#check-group] How many rows does this grouped query return?

*Checkpoint*

**Question:** A table of 40 deliveries covers 6 couriers; courier K9 made only 1 delivery. `SELECT courier_id, COUNT(*) FROM deliveries GROUP BY courier_id HAVING COUNT(*) > 1`. How many rows come back?

- A. 39
- B. 5
- C. 6
- D. 0

#### [day2#lab-2-3] Questions 8 to 11: groups

Lab 2.3 · 35 min

Predict, then answer four grouping questions: orders per store, busy customers, months and best-selling products; save them to your answer file

[D2_3_questions_8_to_11.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_3_questions_8_to_11.ipynb)

- [ ] Write a prediction for each of the four questions (5 min)
- [ ] Question 8: delivered orders per store (7 min)
- [ ] Question 9: customers with many orders, using HAVING (8 min)
- [ ] Question 10: orders and distinct customers per month (7 min)
- [ ] Question 11: products on many order lines (5 min)
- [ ] Save the part file (3 min)
- [ ] ✱ Stretch: Explain why COUNT(discount) and COUNT(\*) differ on the order lines

### Session 4: Inner, outer, semi and anti joins

#### [day2#s4] Inner, outer, semi and anti joins

*Session 4*

- Predict the rows an inner and a left join return on small tables
- Find rows without a partner with an anti join
- Keep rows that have a partner without multiplying them, with a semi join

#### [day2#inner-join] An inner join keeps only the pairs of rows that match

*Inner join*

```sql
-- file: returns desk
SELECT t.return_id, i.result
FROM returns t
JOIN inspections i
  ON i.return_id = t.return_id;
-- 4 rows
```

- T1 once, T2 twice, T5 once: **4 rows**
- T3 and T4 were never inspected: **gone**
- The ON condition says which rows belong together

> **Two silent effects.** Rows without a partner disappear; rows with several partners repeat.

#### [day2#left-join] A left join keeps every row of the left table, matched or not

*Outer joins*

| return_id | result |
| --- | --- |
| T1 | pass |
| T2 | pass |
| T2 | fail |
| T3 | NULL |
| T4 | NULL |
| T5 | pass |

`returns LEFT JOIN inspections`: **6 rows**. The unmatched returns come back with NULL in every column of the right side. A right join keeps the right side; a full join keeps both.

#### [day2#anti-join] An anti join keeps the rows that have no partner

*Anti join*

```sql
-- file: returns desk
SELECT t.return_id
FROM returns t
WHERE NOT EXISTS (
  SELECT 1 FROM inspections i
  WHERE i.return_id = t.return_id
);
-- T3, T4
```

- "Returns never inspected", "products never sold", "customers who never ordered"
- Also written as a left join with `WHERE i.return_id IS NULL`
- Avoid `NOT IN (subquery)`: one NULL in it empties the result

#### [day2#semi-join] A semi join keeps each row that has a partner, once

*Semi join*

```sql
-- file: returns desk
SELECT COUNT(*)
FROM returns t
WHERE EXISTS (
  SELECT 1 FROM inspections i
  WHERE i.return_id = t.return_id
);
-- 3
```

- **Not the same as an inner join.** The inner join counted 4 rows: T2 twice. "How many returns were inspected?" is 3. EXISTS never repeats a row.

#### [day2#which-join] Choose the join from the question's words

*Choosing*

| The question says | Join |
| --- | --- |
| "each ... with its ..." | inner |
| "every ..., including those without ..." | left |
| "... that never ...", "... without any ..." | anti: `NOT EXISTS` |
| "... that had at least one ..." | semi: `EXISTS` |

#### [day2#check-join] How many rows does the left join return?

*Checkpoint*

**Question:** `couriers` has 4 rows. `shifts` has 7 rows: courier A has 3 shifts, B has 2, C has 2, D has none. How many rows does `couriers LEFT JOIN shifts` return?

- A. 4
- B. 7
- C. 8
- D. 28

#### [day2#lab-2-4] Questions 12 to 15: joins

Lab 2.4 · 35 min

Predict, then answer four questions, one for each kind of join; save them to your answer file

[D2_4_questions_12_to_15.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D2_4_questions_12_to_15.ipynb)

- [ ] Write a prediction for each of the four questions (5 min)
- [ ] Question 12: delivered orders per store region (7 min)
- [ ] Question 13: customers and never-ordered customers per region (8 min)
- [ ] Question 14: active products that were never sold (7 min)
- [ ] Question 15: customers with at least one failed attempt (5 min)
- [ ] Save the part file (3 min)
- [ ] ✱ Stretch: Write question 13 with a left join and with NOT EXISTS, and say which one a reader understands first

#### [day2#wrap-up] Three things to keep from Day 2

*Wrap-up*

- **NULL is unknown.** WHERE keeps only true rows. Ask IS NULL, or COALESCE on purpose.
- **Groups set the grain.** One row per group; conditions on counts go in HAVING.
- **Joins drop and repeat.** Choose inner, left, anti or semi from the question's words.

#### [day2#next] Day 3: count once, build in steps, then windows

*Next*

- Finish questions 5 to 15 if you did not: about 30 minutes
- Keep `answers/`: the checker runs over all twenty tomorrow
- Read `data/revenue_rule.md` once before Day 3

## Day 3: Combining safely, then windows

Count once, build in steps, then rank and compare without losing rows

#### [day3#title] Combining safely, then windows

*SDAIA Academy · SQL and Relational Data*

Day 3: Count once, build in steps, then rank and compare without losing rows

Data & AI Foundations Track · 4 teaching days + capstone day · 4 sessions · 4 labs · FND-DAT-101

#### [day3#agenda] Combining safely, then windows

*Today*

- **Session 1 · Join fan-out and double counting**: A join to a many side repeats the rows of the one side, and every sum over them grows
- **Session 2 · Subqueries and common table expressions**: Build an answer in named steps, each of which you can run and check on its own
- **Session 3 · Partitions, ranking, lag and lead**: A window computes over related rows and keeps every row: PARTITION BY, ORDER BY, RANK, LAG
- **Session 4 · Running and moving aggregates**: Running totals, week-on-week change and seven-day averages, and the frame that decides them

#### [day3#review-day2] How many rows does this query return?

*Review of Day 2*

**Question:** A `branches` table has 5 rows; 2 branches have no `region`. `SELECT COUNT(*) FROM branches WHERE region NOT IN ('North', NULL)`.

- A. 3
- B. 0
- C. 5
- D. 2

### Session 1: Join fan-out and double counting

#### [day3#s1] Join fan-out and double counting

*Session 1*

- Detect fan-out by counting rows before and after a join
- Aggregate to the right grain before joining
- Explain a wrong total from the grain of each table it joined

#### [day3#fan-out-picture] A join to a many side repeats every row of the one side

*Fan-out*

| return_id | refund | inspection |
| --- | --- | --- |
| T1 | 12.00 | pass |
| T2 | 30.50 | pass |
| T2 | 30.50 | fail |
| T5 | 19.00 | pass |

- T2 was inspected twice, so its refund now sits on **two rows**
- Every column of `returns` is repeated, not only the key
- Nothing warns you: the query runs, the numbers look plausible

#### [day3#fan-out-sum] Every sum over a fanned-out join grows

*Double counting*

- **92.00** SUM(refund) after the join
- **61.50** the refunds of the inspected returns

30.50 counted twice. And T3 and T4 are gone: the join also **drops** rows with no partner. A fanned-out sum can be too high and too low at once.

The returns desk (`_tools/slide_examples.py`).

#### [day3#detect-fan-out] Count rows before and after every join

*Detect it*

```sql
-- file: returns desk
SELECT (SELECT COUNT(*) FROM returns)              AS before,
       (SELECT COUNT(*) FROM returns t
          JOIN inspections i ON i.return_id = t.return_id) AS after;
-- before 5, after 4: rows were dropped AND repeated
```

- After > before: some rows repeat
- After < before: some rows lost their partner
- Equal is not proof: drops and repeats can cancel out, as they nearly do here

#### [day3#aggregate-first] Bring each side to the grain of the question before joining

*The fix*

```sql
-- file: returns desk
WITH insp AS (                       -- one row per return
  SELECT return_id, COUNT(*) AS inspections
  FROM inspections GROUP BY return_id
)
SELECT SUM(t.refund), SUM(insp.inspections)
FROM returns t
JOIN insp ON insp.return_id = t.return_id;
-- 61.50 and 4: one row per return on both sides
```

> **Or filter instead of joining.** `WHERE return_id IN (SELECT ...)` or `EXISTS` keeps each return once.

#### [day3#distinct-is-not-a-fix] SUM(DISTINCT ...) hides fan-out by accident, and breaks on equal values

*A tempting shortcut*

- **Looks right here.** `SUM(DISTINCT refund)` on the joined rows gives 61.50: T2's repeat collapses.
- **Wrong tomorrow.** Two different returns with a refund of 12.00 collapse into one. The total is short, and nothing says so.

> **Rule.** DISTINCT removes duplicate values, not duplicate rows of the grain you meant. Fix the grain instead.

#### [day3#grain-before-join] Before every join, write the grain of both sides and of the result

*The habit*

| Left | Right | Result | Sum left? |
| --- | --- | --- | --- |
| return | reason | return | yes |
| return | inspection | inspection | **no** |
| return | return (aggregated) | return | yes |

Each grain is "one row per ..." the word in the cell. "Sum left?": is it safe to sum the left side's money after the join?

#### [day3#check-fan-out] Why is the total fee too high?

*Checkpoint*

**Question:** A clinic sums appointment fees after joining `appointments` (one row per appointment) to `reminders` (one row per reminder sent). Some appointments got three reminders. The total is 40% above the ledger.

- A. Fees left NULL are counted as zero
- B. The join drops appointments with no reminder
- C. Fees are rounded to two decimals
- D. Each fee is repeated once per reminder

#### [day3#lab-3-1] Questions 16 and 17: count once

Lab 3.1 · 35 min

See a sum grow when order lines meet delivery attempts, then answer two questions that need lines and attempts together without double counting; save them to your answer file

[D3_1_questions_16_and_17.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_1_questions_16_and_17.ipynb)

- [ ] Count rows before and after joining delivery attempts (6 min)
- [ ] Write a prediction for each of the two questions (4 min)
- [ ] Question 16: line value of orders that needed a second attempt (10 min)
- [ ] Question 17: orders and attempts per store in one result (10 min)
- [ ] Save the part file (5 min)
- [ ] ✱ Stretch: Find the share by which the naive sum of line values overstates the true one

### Session 2: Subqueries and common table expressions

#### [day3#s2] Subqueries and common table expressions

*Session 2*

- Use a subquery in WHERE and in FROM
- Write a query as a chain of common table expressions
- Check each step of a chain before trusting the last

#### [day3#subquery-where] A subquery is a query inside another, used as a value, a list or a table

*Subqueries*

| Where | Returns | Returns desk example |
| --- | --- | --- |
| In `WHERE x > (...)` | one value | refunds above the average refund |
| In `WHERE x IN (...)` | a list | returns that were inspected |
| In `FROM (...)` | a table | items per return, then their average |

#### [day3#correlated] A correlated subquery is evaluated for each row of the outer query

*Per row*

```sql
-- file: returns desk
SELECT t.return_id, t.refund
FROM returns t
WHERE t.refund > (SELECT AVG(r.refund)
                  FROM returns r
                  WHERE r.reason_code = t.reason_code);  -- the average of its own reason
```

- The inner query refers to `t`, the row being tested
- "Above the average of its own group" is the typical use
- The same answer can be written as a join to a grouped table: often clearer

#### [day3#cte-names-steps] WITH names each step, so a long answer reads top to bottom

*Common table expressions*

```sql
-- file: returns desk
WITH items AS (                    -- step 1: one row per return
  SELECT return_id, SUM(qty) AS units
  FROM return_items
  GROUP BY return_id
)
SELECT AVG(units) FROM items;      -- step 2: 3.0 units per return
```

> **Read it as a recipe.** Each name is a table you could look at on its own. Several steps are separated by commas: `WITH a AS (...), b AS (...)`.

#### [day3#check-each-step] Run each step before you trust the last one

*The method*

1. **1 · First step alone** select from it; look at 5 rows; count them
2. **2 · Its grain** one row per what? is a key unique?
3. **3 · Add the next step** and repeat
4. **4 · The final select** compare with your prediction

#### [day3#rule-outside-schema] Some rules live outside the schema, and the query must carry them

*Business rules*

- **What the schema says.** Columns, types, keys, a status column with three values.
- **What it does not say.** Which statuses count as revenue, what an empty discount means, which date books the money.

The finance controller keeps that in `data/revenue_rule.md`. A query that ignores it runs without error and returns a number nobody in finance would sign.

#### [day3#rule-to-steps] Turn each point of a rule into one named step

*From rule to query*

| Returns desk rule | Step |
| --- | --- |
| Only returns with a decided refund | `decided AS (... WHERE refund IS NOT NULL)` |
| Book on the inspection date, not the receipt date | `booked AS (... JOIN inspections ...)` |
| Count a return once, even if inspected twice | take the first inspection per return |

A parallel rule of the returns desk; the finance rule of the labs is yours to turn into steps.

#### [day3#check-cte] Where is the error in this chain?

*Checkpoint*

**Question:** A hotel's chain: `stays` (one row per stay) joined to `charges` (one row per charge), then `SUM(nightly_rate * nights)` per month. The result is far above the ledger.

- A. The final GROUP BY month
- B. The join of stays to charges before summing stay values
- C. Using WITH instead of a subquery
- D. Multiplying rate by nights

#### [day3#lab-3-2] Questions 18 to 20, and the checker

Lab 3.2 · 35 min

Predict, then answer the last three questions in steps, one of them by the finance rule; then run the automatic checker over all twenty

[D3_2_questions_18_to_20.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_2_questions_18_to_20.ipynb)

- [ ] Write a prediction for each of the three questions (4 min)
- [ ] Question 18: products above their category's average price (8 min)
- [ ] Question 19: net revenue by month of delivery, by the finance rule (9 min)
- [ ] Question 20: the five customers with the highest net revenue (8 min)
- [ ] Run the checker over all your part files and fix one failure (6 min)
- [ ] ✱ Stretch: Rewrite question 19 as one query without common table expressions and compare how easy each is to check

### Session 3: Partitions, ranking, lag and lead

#### [day3#s3] Partitions, ranking, lag and lead

*Session 3*

- Write a window with a partition and an ordering
- Choose between ROW_NUMBER, RANK and DENSE_RANK at ties
- Compare a row with the one before it using LAG

#### [day3#window-keeps-rows] A window computes over related rows and keeps every row

*Window functions*

- **GROUP BY.** Five returns in, three rows out: one per reason. The detail is gone.
- **OVER (...).** Five returns in, five rows out, each with a value computed from its group.

```sql
-- file: returns desk
SELECT return_id, reason_code, refund,
       SUM(refund) OVER (PARTITION BY reason_code) AS reason_total
FROM returns;
```

#### [day3#partition-and-order] PARTITION BY says which rows belong together; ORDER BY says in what sequence

*The two clauses*

| Clause | Question it answers | Without it |
| --- | --- | --- |
| `PARTITION BY region` | Whose rows are compared? | all rows form one window |
| `ORDER BY day` | Which row comes before which? | ranks and LAG have no meaning |

> **Say the partition in a comment.** "-- partition: one ranking per region, so ..." The window checker of the labs asks for exactly this.

#### [day3#three-rankings] ROW_NUMBER, RANK and DENSE_RANK differ only at ties

*Ranking*

| product (units) | ROW_<br>NUMBER | RANK | DENSE_<br>RANK |
| --- | --- | --- | --- |
| X-101 (4) | 1 | 1 | 1 |
| X-412 (4) | 2 | 1 | 1 |
| X-118 (3) | 3 | 3 | 2 |
| X-205 (3) | 4 | 3 | 2 |
| X-330 (1) | 5 | 5 | 3 |

Returned units per product at the returns desk, ordered by units from the most.

#### [day3#top-n-per-group] Rank inside each partition, then keep the first places

*Top N per group*

```sql
-- file: returns desk
WITH ranked AS (
  SELECT reason_code, return_id, refund,
         RANK() OVER (PARTITION BY reason_code ORDER BY refund DESC) AS place
  FROM returns
)
SELECT * FROM ranked WHERE place = 1;   -- the largest refund of each reason
```

> **What goes wrong.** `WHERE RANK() OVER (...) = 1` is refused: windows are computed after WHERE. Rank in one step, filter in the next, or use `QUALIFY`.

#### [day3#lag-lead] LAG reads the previous row of the window; LEAD reads the next

*Neighbouring rows*

| return_id | received_on | days_since |
| --- | --- | --- |
| T1 | 2026-05-02 | NULL |
| T2 | 2026-05-02 | 0 |
| T3 | 2026-05-03 | 1 |
| T4 | 2026-05-04 | 1 |
| T5 | 2026-05-06 | 2 |

```sql
-- file: returns desk
received_on
  - LAG(received_on) OVER (
      ORDER BY received_on, return_id)
  AS days_since
```

The first row has no previous row: **NULL**. With a partition, every partition's first row is NULL.

#### [day3#check-rank] Which ranking keeps every tied product in a "top three"?

*Checkpoint*

**Question:** Sales per product in each region: in the West, two products tie for third place. The manager wants both shown, and the next product, if any, to be fifth.

- A. ROW_NUMBER() and place <= 3
- B. DENSE_RANK() and place <= 3
- C. RANK() and place <= 3
- D. ORDER BY sales DESC LIMIT 3

#### [day3#lab-3-3] Window drills 1: top items per region

Lab 3.3 · 30 min

Rank products within each region, compare three ranking functions at ties, and measure the days between a customer's orders with LAG; each partition explained in a comment

[D3_3_window_drills_1.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_3_window_drills_1.ipynb)

- [ ] Drill 1: the top three products per region by quantity (10 min)
- [ ] Drill 2: ROW_NUMBER, RANK and DENSE_RANK on the same ties (6 min)
- [ ] Drill 3: days since the customer's previous order, with LAG (8 min)
- [ ] Write the partition comments and save the drills (6 min)
- [ ] ✱ Stretch: Return the top three per region with QUALIFY and with a subquery, and confirm they agree

### Session 4: Running and moving aggregates

#### [day3#s4] Running and moving aggregates

*Session 4*

- Compute a running total that restarts in each partition
- Compute a week-on-week change with LAG over weekly totals
- Choose a ROWS or a RANGE frame when days are missing

#### [day3#running-total] SUM with an ORDER BY in the window adds up as it goes

*Running totals*

| return_id | refund | running |
| --- | --- | --- |
| T1 | 12.00 | 12.00 |
| T2 | 30.50 | 42.50 |
| T3 | 8.25 | 50.75 |
| T4 | NULL | 50.75 |
| T5 | 19.00 | 69.75 |

- `SUM(refund) OVER (ORDER BY return_id)`
- T4's unknown refund adds nothing: the total stays
- Add `PARTITION BY month` and it restarts each month

#### [day3#period-change] For week-on-week change, aggregate to weeks first, then LAG

*Comparing periods*

1. **1 · Daily rows** one row per store and day
2. **2 · Weekly totals** GROUP BY store, week
3. **3 · LAG over weeks** PARTITION BY store ORDER BY week
4. **4 · Change** this week minus the previous

> **What goes wrong.** A first or last week with fewer days looks like a fall or a jump. Say so beside the number, or leave partial weeks out.

#### [day3#frames] The frame decides which rows a moving average uses

*Frames*

| Frame | Means |
| --- | --- |
| `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` | this row and the six rows before it |
| `RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW` | every row whose date is within the last seven days |

They agree when every day has exactly one row. They part when a day is missing.

#### [day3#rows-vs-range] With a missing day, ROWS reaches too far back; RANGE does not

*Missing days*

| received_on | day's refunds | 2 rows | 2 days |
| --- | --- | --- | --- |
| 2026-05-02 | 42.50 | 42.50 | 42.50 |
| 2026-05-03 | 8.25 | 25.38 | 25.38 |
| 2026-05-04 | 0.00 | 4.13 | 4.13 |
| 2026-05-06 | 19.00 | 9.50 | 19.00 |

No return arrived on 5 May. "2 rows" averages 6 May with 4 May; "2 days" averages only 6 May, the one day in its window that has a row.

#### [day3#check-frame] Which seven-day average is right after a closed weekend?

*Checkpoint*

**Question:** A pharmacy's daily sales table has no rows for two closed days. For each day, the report wants the average daily sales of the days that had sales within the last seven calendar days, that day included.

- A. AVG OVER (ORDER BY day RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW)
- B. AVG OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
- C. AVG OVER (PARTITION BY day)
- D. AVG with GROUP BY week

#### [day3#lab-3-4] Window drills 2: weeks and seven days

Lab 3.4 · 35 min

From the daily order table, compute week-on-week change per store, a running total within each month and seven-day averages that stay right across closed days; run the window checker

[D3_4_window_drills_2.ipynb](https://sdaiaacademy.github.io/fnd-dat-101/labs/D3_4_window_drills_2.ipynb)

- [ ] Drill 4: weekly orders per store and the change from the week before (10 min)
- [ ] Drill 5: running net sales per store within each month (8 min)
- [ ] Drill 6: seven-day average net sales, ROWS against RANGE (10 min)
- [ ] Save the drills and run the window checker (7 min)
- [ ] ✱ Stretch: Fill the closed days with zero rows from a calendar and compare the three seven-day averages

#### [day3#wrap-up] Three things to keep from Day 3

*Wrap-up*

- **Count once.** Bring each side to the question's grain before joining.
- **Build in steps.** Name each step, run it alone, carry the business rule.
- **Windows keep rows.** Partition, order, frame: say each in a comment.

#### [day3#next] Day 4: building and checking

*Next*

- Bring the twenty questions to 16 or more and finish the window drills: about an hour
- Tomorrow: constrained tables, a view for analysts, query plans, and ten generated queries on trial

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

## Capstone: Capstone: the business orders brief

For each participant: five minutes of live adaptation of one query, then two of questions on the assumptions note

#### [capstone#title] Capstone: the business orders brief

*SDAIA Academy · SQL and Relational Data*

Capstone: For each participant: five minutes of live adaptation of one query, then two of questions on the assumptions note

Data & AI Foundations Track · 4 teaching days + capstone day · 5 min talk and demo · 2 min Q&A · FND-DAT-101

#### [capstone#agenda] How the day runs

*Capstone day*

- **Opening**: the rubric and the format
- **Timed check**: assistant off, on paper
- **Final preparation**: finish the repository, run the tests, push
- **Live adaptations**: one query each, then questions on the assumptions note
- **Reviews and next steps**: peer review, the trainer's review, the follow-up task

#### [capstone#rubric] The rubric

*How the repository is scored · 30% of the course*

| Item | Value |
| --- | --- |
| Correct: the ten queries match the key on the full data | 35% |
| Tests against a fixture checked by hand, and they pass | 20% |
| Grain stated for every query and join | 15% |
| Assumptions note: every rule stated, applied and traced | 15% |
| Verification log of generated SQL | 10% |
| Minimal exposure: no personal data a question does not need | 5% |

#### [capstone#format] Five minutes to adapt one query live, then two minutes of questions

*Format*

- **1 · The change.** The trainer reads a changed version of one of your ten questions.
- **2 · The query.** You change it, add a fixture row if needed, and run its test.
- **3 · The reason.** You say what changed in the grain or the rules.

> **Then two minutes on your assumptions note.** Expect "where is this rule applied?" and "why did you decide this?"

#### [capstone#timed-check] Ten questions · 40 minutes

*Timed check · assistant off*

Two printed tables, ten short questions. Predict, explain, write one query on paper.

#### [capstone#final-prep] Final preparation · 120 minutes

*Before the first adaptation*

Run `uv run pytest capstone/tests -q`, fill in the notes, commit and push.

#### [capstone#running-order] Who adapts when

*Running order*

| # | Participant | Query to adapt | # | Participant | Query to adapt |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  | 9 |  |  |
| 2 |  |  | 10 |  |  |
| 3 |  |  | 11 |  |  |
| 4 |  |  | 12 |  |  |
| 5 |  |  | 13 |  |  |
| 6 |  |  | 14 |  |  |
| 7 |  |  | 15 |  |  |
| 8 |  |  | 16 |  |  |

#### [capstone#now-presenting] Now adapting

*Now adapting*

#### [capstone#peer-review] Run a classmate's tests and read one of their queries against the rules

*Peer review · 50 minutes*

- Clone the repository of the participant after you in the running order
- Run its tests; pick one query and check its grain comment against the query
- Write one strength, one question and one suggestion as an issue on their repository

#### [capstone#review] What the repositories showed

*Trainer review*

- **Strongest patterns.** What several repositories got right.
- **Common gaps.** The traps most answers fell into.
- **One surprise.** Something nobody expected.

#### [capstone#follow-up] Two new questions from the business orders service, answered the same way

*Follow-up task · within two weeks*

- The trainer sends two questions after the course; you add `q11.sql` and `q12.sql` to your repository
- Each with its grain comment, its expected rows worked by hand and a passing test
- About an hour; the commits on your repository are the record that it was done

#### [capstone#what-next] Keep going

*After the course*

- **Your repository stays yours:** keep its tests running when you change a query
- **Next Academy course:** FND-DAT-102 Data Wrangling with DataFrames, then FND-DAT-103 Data Formats, Interfaces and Quality Checks

#### [capstone#thanks] Thank you

*SDAIA Academy*

SQL and Relational Data
