"""Load the business orders tables and run the ten queries.

    uv run python capstone/cap.py                 # from labs/: run every query on the full data, write results/
    uv run python capstone/cap.py q03             # one query
    uv run python capstone/cap.py --fixture q03   # one query on the fixture

The tests (capstone/tests/) use the same loader on the fixture.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
FULL = HERE / "data" / "full"
FIXTURE = HERE / "fixture"
QUERIES = HERE / "queries"
RESULTS = HERE / "results"

DDL = """
CREATE TABLE accounts (
  account_id    VARCHAR PRIMARY KEY,
  segment       VARCHAR NOT NULL CHECK (segment IN ('office', 'school', 'clinic', 'restaurant')),
  region        VARCHAR NOT NULL,
  opened_on     DATE NOT NULL,
  contact_name  VARCHAR,
  contact_phone VARCHAR,
  contact_email VARCHAR,
  credit_limit  DECIMAL(10,2) NOT NULL
);
CREATE TABLE sites (
  site_id    VARCHAR PRIMARY KEY,
  account_id VARCHAR NOT NULL REFERENCES accounts (account_id),
  region     VARCHAR NOT NULL,
  is_active  BOOLEAN NOT NULL
);
CREATE TABLE items (
  item_id   VARCHAR PRIMARY KEY,
  item_name VARCHAR NOT NULL,
  category  VARCHAR NOT NULL,
  is_active BOOLEAN NOT NULL
);
CREATE TABLE price_list (
  item_id    VARCHAR NOT NULL REFERENCES items (item_id),
  valid_from DATE NOT NULL,
  valid_to   DATE,
  unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
  PRIMARY KEY (item_id, valid_from)
);
CREATE TABLE bulk_orders (
  order_id   VARCHAR PRIMARY KEY,
  account_id VARCHAR NOT NULL REFERENCES accounts (account_id),
  site_id    VARCHAR NOT NULL REFERENCES sites (site_id),
  ordered_on DATE NOT NULL,
  status     VARCHAR NOT NULL CHECK (status IN ('open', 'closed', 'cancelled'))
);
CREATE TABLE bulk_lines (
  order_id    VARCHAR NOT NULL REFERENCES bulk_orders (order_id),
  line_no     INTEGER NOT NULL,
  item_id     VARCHAR NOT NULL REFERENCES items (item_id),
  qty_ordered INTEGER NOT NULL CHECK (qty_ordered > 0),
  PRIMARY KEY (order_id, line_no)
);
CREATE TABLE shipments (
  shipment_id VARCHAR PRIMARY KEY,
  order_id    VARCHAR NOT NULL,
  line_no     INTEGER NOT NULL,
  shipped_on  DATE NOT NULL,
  qty_shipped INTEGER NOT NULL CHECK (qty_shipped > 0),
  outcome     VARCHAR NOT NULL CHECK (outcome IN ('delivered', 'returned')),
  FOREIGN KEY (order_id, line_no) REFERENCES bulk_lines (order_id, line_no)
);
"""
TABLES = ["accounts", "sites", "items", "price_list", "bulk_orders", "bulk_lines", "shipments"]


def connect(folder: Path = FULL):
    """The seven tables from a folder of CSV files, in memory."""
    if folder == FULL and not (FULL / "shipments.csv").exists():
        sys.path.insert(0, str(HERE))
        import prepare_capstone
        prepare_capstone.main([])
    con = duckdb.connect()
    con.execute(DDL)
    for t in TABLES:
        con.execute(f"INSERT INTO {t} SELECT * FROM read_csv(?, header = true, nullstr = '', auto_detect = true)",
                    [str(folder / f"{t}.csv")])
    return con


def query_text(key: str) -> str:
    return (QUERIES / f"{key}.sql").read_text(encoding="utf-8")


def is_blank(sql: str) -> bool:
    body = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    return not body.strip().rstrip(";").strip()


def run(key: str, con):
    sql = query_text(key)
    if is_blank(sql):
        return None, None
    cur = con.execute(sql.strip().rstrip(";"))
    return [d[0] for d in cur.description], cur.fetchall()


def main(argv) -> int:
    fixture = "--fixture" in argv
    keys = [a for a in argv if not a.startswith("--")] or [f"q{i:02d}" for i in range(1, 11)]
    con = connect(FIXTURE if fixture else FULL)
    for key in keys:
        cols, rows = run(key, con)
        if cols is None:
            print(f"{key}: not written yet")
            continue
        print(f"{key}: {len(rows)} rows")
        for r in rows[:10]:
            print("   ", r)
        if not fixture:
            RESULTS.mkdir(exist_ok=True)
            with (RESULTS / f"{key}.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(cols)
                w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
