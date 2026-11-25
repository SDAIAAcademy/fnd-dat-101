# Capstone: the business orders brief

The grocery delivery company also supplies organisations in bulk: offices, schools, clinics and
restaurants order cases of paper, cleaning goods, first-aid supplies, stationery and drinks for
their sites. The head of the business orders service has sent ten questions about the second
half of 2026. You answer them in a repository of tested SQL.

The data is new to you: seven tables you have not seen in the labs, synthetic, with the same
kind of traps. Everything in it is invented. Accounts are organisations known only by a code and
a segment; their contact person appears as `Synthetic Contact 0001` with a phone and an e-mail
that are invalid on purpose.

## Start

1. Make a new repository of your own on GitHub, public, and copy this folder into it. Commit
   the starting files first: the history is part of the submission.
2. From `labs/` of the course (or any folder with DuckDB 2.0.1 and pytest), write the data:

   ```
   uv run python capstone/prepare_capstone.py
   ```

   It writes `capstone/data/full/` (about 3 MB, seven CSV files) and prints a digest, which must
   read the same as `data/full.sha256`. Do not commit `data/full/`: it is rebuilt from the
   script.
3. Run the tests: `uv run pytest capstone/tests -q`. All ten are skipped until you write them.

## The tables

| Table | One row per | Columns |
|---|---|---|
| accounts | business customer | account_id, segment (office, school, clinic, restaurant), region, opened_on, contact_name, contact_phone, contact_email, credit_limit |
| sites | delivery site of an account | site_id, account_id, region, is_active |
| items | item in the catalogue | item_id, item_name, category, is_active |
| price_list | item and period of a price | item_id, valid_from, valid_to (empty: still valid), unit_price |
| bulk_orders | order | order_id, account_id, site_id (where it is delivered), ordered_on, status (open, closed, cancelled) |
| bulk_lines | line of an order | order_id, line_no, item_id, qty_ordered |
| shipments | shipment of part or all of a line | shipment_id, order_id, line_no, shipped_on, qty_shipped, outcome (delivered, returned) |

A line can be shipped in several shipments. Prices are not stored on the lines.

## The rules

The finance controller's rules for revenue, kept outside the schema like the revenue rule of
the labs:

- **R1** Cancelled orders are left out of every answer.
- **R2** Revenue comes from delivered shipments only; a returned shipment earns nothing. Units
  shipped (q02, q04) count every shipment, returned or not.
- **R3** A line's unit price is the price-list row of its item valid on the **order date**:
  `valid_from` on or before it, and `valid_to` empty or after it. `valid_to` is the first day
  the price no longer applies.
- **R4** Revenue of a shipment = quantity shipped × unit price, less the segment's discount:
  schools 10%, clinics 5%, offices and restaurants none.
- **R5** Revenue is booked in the month of the **shipment date**. "July to December 2026" means
  shipments dated 1 July to 31 December 2026 (q03, q06, q07, q09).
- **R6** Round amounts to two decimals at the end; the fill rate to three.

## The ten questions

Write one query per file in `queries/`, with the columns named exactly as below and the header
comment filled in.

| # | Question | Columns, in this order |
|---|---|---|
| q01 | How many accounts are there per segment, and how many of them placed at least one order that was not cancelled? | segment, accounts, ordering_accounts |
| q02 | Per item category, how many units were ordered and how many shipped? Only categories with at least one ordered line. | category, units_ordered, units_shipped |
| q03 | What was the revenue of each month, July to December 2026? | month (as 2026-07), revenue |
| q04 | What is the fill rate of closed orders (units shipped over units ordered) per region of the **delivery site**? | region, fill_rate |
| q05 | Per month of ordering, how many closed orders had their last shipment more than 7 days after the order date? | month, orders_late |
| q06 | Which five items brought the most revenue, July to December 2026? Keep ties: every item ranked 5 or better. | rank, item_id, item_name, revenue |
| q07 | Per segment and month, July to December 2026, what was the revenue and its change against the segment's previous month in the result (empty for its first month)? | segment, month, revenue, change_vs_previous_month |
| q08 | Per category, how many active items with a price valid on 31 December 2026 were never on a line of an order that was not cancelled? | category, items |
| q09 | In which months, July to December 2026, did an account's revenue exceed its credit limit? | account_id, month, revenue |
| q10 | Per segment, what is the average revenue of a closed order, counting all its delivered shipments whatever their date? A closed order with no delivered shipment counts as 0. | segment, avg_revenue_per_order |

Order every answer by its first columns. None of the questions needs a contact's name, phone or
e-mail: an answer that returns one loses the marks for minimal exposure.

## What you hand in

A link to your public repository, with its history, holding:

- `queries/q01.sql` to `queries/q10.sql`, each with its grain comment filled in;
- `fixture/`: the small tables your tests run on. The starting fixture has the traps of the
  brief in a few rows; extend it when a question needs a case it lacks;
- `tests/expected/q01.csv` to `q10.csv`: the rows **you worked out by hand** from the fixture,
  header first (the column names), then one line per row; an empty cell is NULL. The tests run
  each query on the fixture and compare;
- `ASSUMPTIONS.md`: every rule you applied, R1 to R6 and the ones you had to decide, each with
  the queries that use it;
- `VERIFICATION_LOG.md`: every query an assistant wrote or changed, with the test that caught or
  passed it. If no assistant was used, say so.

`uv run python capstone/cap.py` runs your ten queries on the full data and writes
`results/q01.csv` to `q10.csv` (not committed). The trainer runs the same command on a clone of
your repository and compares the results with the key.

## Using an assistant

AI-full: you may use an approved assistant for any part, and you log it. Give it the table
descriptions above and the rules, never rows of the data. A generated query counts when it passes
your hand-checked test, and the log says so.

## On the capstone day

- **Timed check, 40 minutes, assistant off**: short questions on printed tables, like the
  predictions of the labs.
- **Live adaptation, 5 minutes**: the trainer changes one of the ten questions; you change your
  query, run its test and say what changed in the grain or the rules.
- **Questions on your assumptions note, 2 minutes.**

The rubric is in the course README.
