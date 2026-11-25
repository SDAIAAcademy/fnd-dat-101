---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/slides/day3.html"
---

# SQL and Relational Data

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
