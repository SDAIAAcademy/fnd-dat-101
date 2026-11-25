# SQL and Relational Data: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository, installs the two packages and writes the data.
- Locally: install uv, clone the repository, then from `labs/` run `uv run --with jupyterlab jupyter lab` and open a notebook. The first run writes the six synthetic tables (`prepare_data.py`, about ten seconds) and builds `data/delivery.duckdb`.
- Start with `00_setup_check.ipynb`: it ends with **setup ok**.

You write SQL between the triple quotes of each cell marked ✏️. A cell left blank shows the reference result, so the next cells still run. The reference version of every notebook is in `solutions/`.

| Day | Session | Lab | Notebook |
|---|---|---|---|
| Day 1 | Session 1 · Tables, types, keys and constraints | Lab 1.1 · Six tables and their keys | [`D1_1_tables_and_keys.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D1_1_tables_and_keys.ipynb) |
| Day 1 | Session 2 · Grain and cardinality | Lab 1.2 · The annotated schema | [`D1_2_annotated_schema.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D1_2_annotated_schema.ipynb) |
| Day 1 | Session 3 · Normal forms, wide tables and embedded engines | Lab 1.3 · One wide table, and what it repeats | [`D1_3_wide_table.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D1_3_wide_table.ipynb) |
| Day 1 | Session 4 · Filters, sorting and expressions | Lab 1.4 · Questions 1 to 4, predicted first | [`D1_4_questions_1_to_4.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D1_4_questions_1_to_4.ipynb) |
| Day 2 | Session 1 · CASE expressions and set operations | Lab 2.1 · Questions 5 to 7: bands and sets | [`D2_1_questions_5_to_7.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D2_1_questions_5_to_7.ipynb) |
| Day 2 | Session 2 · NULL and three-valued logic | Lab 2.2 · Predict, then run: twelve NULL comparisons | [`D2_2_null_predictions.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D2_2_null_predictions.ipynb) |
| Day 2 | Session 3 · Grouping and having | Lab 2.3 · Questions 8 to 11: groups | [`D2_3_questions_8_to_11.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D2_3_questions_8_to_11.ipynb) |
| Day 2 | Session 4 · Inner, outer, semi and anti joins | Lab 2.4 · Questions 12 to 15: joins | [`D2_4_questions_12_to_15.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D2_4_questions_12_to_15.ipynb) |
| Day 3 | Session 1 · Join fan-out and double counting | Lab 3.1 · Questions 16 and 17: count once | [`D3_1_questions_16_and_17.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D3_1_questions_16_and_17.ipynb) |
| Day 3 | Session 2 · Subqueries and common table expressions | Lab 3.2 · Questions 18 to 20, and the checker | [`D3_2_questions_18_to_20.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D3_2_questions_18_to_20.ipynb) |
| Day 3 | Session 3 · Partitions, ranking, lag and lead | Lab 3.3 · Window drills 1: top items per region | [`D3_3_window_drills_1.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D3_3_window_drills_1.ipynb) |
| Day 3 | Session 4 · Running and moving aggregates | Lab 3.4 · Window drills 2: weeks and seven days | [`D3_4_window_drills_2.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D3_4_window_drills_2.ipynb) |
| Day 4 | Session 1 · Loading into constrained tables, and transactions | Lab 4.1 · Load the extracts and log every rejected row | [`D4_1_load_with_log.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D4_1_load_with_log.ipynb) |
| Day 4 | Session 2 · Views that limit what is exposed | Lab 4.2 · Label the tables and build the analyst view | [`D4_2_analyst_view.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D4_2_analyst_view.ipynb) |
| Day 4 | Session 3 · Query plans and indexes | Lab 4.3 · Read two plans and watch an index change one | [`D4_3_plans_and_indexes.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D4_3_plans_and_indexes.ipynb) |
| Day 4 | Session 4 · Testing queries against known answers | Lab 4.4 · Ten generated queries against hand-checked answers | [`D4_4_ten_generated_queries.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/fnd-dat-101/blob/main/labs/D4_4_ten_generated_queries.ipynb) |

## Files

| Path | What it is |
|---|---|
| `prepare_data.py` | The data generator: seed 101, standard library only |
| `sqllab.py` | The helpers: the database, `show`, `check` against the reference, the checkers of the assessed labs |
| `data/twenty_questions.md` | The twenty business questions of labs 1.4 to 3.2 |
| `data/revenue_rule.md` | The finance rule for net revenue, kept outside the schema |
| `data/mini/` | Six tiny tables to print and predict from |
| `data/extracts/` | The July extracts with seeded defects, for Day 4 |
| `data/july/` | The July tables as a correct load leaves them, for lab 4.2 |
| `data/verification/` | The ten generated-style queries of lab 4.4 |
| `data/reference/` | The reference results the checks compare with |
| `capstone/` | The business orders brief: its data generator, starting fixture, query templates and tests |
| `answers/` | Written by the labs: your answer files (git ignores them) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks. `uv run python _tools/run_all.py` runs every solution source in strict mode.
