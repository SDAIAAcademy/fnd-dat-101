---
course: "SQL and Relational Data"
code: "FND-DAT-101"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/fnd-dat-101/slides/day2.html"
---

# SQL and Relational Data

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
