"""Helpers for the FND-DAT-101 labs. Participants write SQL; this module does the Python.

    import sqllab as U
    con = U.db()                 # the grocery delivery company's six tables (built on first use)
    U.show("SELECT * FROM stores")
    U.check("q01", SQL_Q01)      # runs your query, prints it, compares it with the reference

Environment variables
  FNDDAT101_STRICT=1   a blank or wrong answer stops the run (used for the solution notebooks)
  FNDDAT101_RECORD=1   the trainer's tool: store results as the reference (labs/_tools/make_reference.py)
"""
from __future__ import annotations

import datetime as _dt
import decimal
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import duckdb

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
FULL = DATA / "full"
DB_FILE = DATA / "delivery.duckdb"
REF = DATA / "reference"
ANSWERS = LABS / "answers"
STRICT = os.environ.get("FNDDAT101_STRICT") == "1"
RECORD = os.environ.get("FNDDAT101_RECORD") == "1"
TABLES = ["stores", "products", "customers", "orders", "order_lines", "deliveries"]

DDL = """
CREATE TABLE stores (
  store_id   VARCHAR PRIMARY KEY,
  region     VARCHAR NOT NULL,
  opened_on  DATE    NOT NULL,
  area_m2    INTEGER CHECK (area_m2 > 0)
);
CREATE TABLE products (
  product_id   VARCHAR PRIMARY KEY,
  product_name VARCHAR NOT NULL,
  category     VARCHAR,
  list_price   DECIMAL(10,2) NOT NULL CHECK (list_price > 0),
  is_active    BOOLEAN NOT NULL
);
CREATE TABLE customers (
  customer_id      VARCHAR PRIMARY KEY,
  joined_on        DATE NOT NULL,
  region           VARCHAR CHECK (region IN ('North','South','East','West','Central')),
  full_name        VARCHAR,
  phone            VARCHAR,
  email            VARCHAR,
  birth_year       INTEGER,
  marketing_opt_in BOOLEAN
);
CREATE TABLE orders (
  order_id     VARCHAR PRIMARY KEY,
  customer_id  VARCHAR NOT NULL REFERENCES customers (customer_id),
  store_id     VARCHAR NOT NULL REFERENCES stores (store_id),
  ordered_at   TIMESTAMP NOT NULL,
  status       VARCHAR NOT NULL CHECK (status IN ('delivered','returned','cancelled')),
  delivery_fee DECIMAL(10,2) NOT NULL
);
CREATE TABLE order_lines (
  order_id    VARCHAR NOT NULL REFERENCES orders (order_id),
  line_no     INTEGER NOT NULL,
  product_id  VARCHAR NOT NULL REFERENCES products (product_id),
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  unit_price  DECIMAL(10,2) NOT NULL,
  discount    DECIMAL(10,2),
  line_status VARCHAR NOT NULL CHECK (line_status IN ('ok','cancelled')),
  PRIMARY KEY (order_id, line_no)
);
CREATE TABLE deliveries (
  delivery_id  VARCHAR PRIMARY KEY,
  order_id     VARCHAR NOT NULL REFERENCES orders (order_id),
  attempt_no   INTEGER NOT NULL,
  courier_id   VARCHAR NOT NULL,
  attempted_at TIMESTAMP NOT NULL,
  outcome      VARCHAR NOT NULL CHECK (outcome IN ('delivered','failed')),
  UNIQUE (order_id, attempt_no)
);
"""

DAILY = """
-- One row per store and order date with at least one order that was not cancelled.
-- net_sales: lines with line_status 'ok' of delivered orders, quantity * unit_price minus the discount.
CREATE TABLE daily_orders AS
SELECT o.store_id,
       CAST(o.ordered_at AS DATE) AS order_date,
       COUNT(DISTINCT o.order_id) AS orders,
       SUM(CASE WHEN o.status = 'delivered' AND l.line_status = 'ok'
                THEN l.quantity * l.unit_price - COALESCE(l.discount, 0) ELSE 0 END) AS net_sales
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY o.store_id, CAST(o.ordered_at AS DATE);
"""


def _say(msg: str) -> None:
    print(msg, flush=True)


# ------------------------------------------------------------------------------ data and databases
def ensure_data() -> None:
    """Write the full tables when they are missing, then check their digest."""
    if not all((FULL / f"{t}.csv").exists() for t in TABLES):
        _say("Writing the synthetic tables (about 10 seconds)...")
        sys.path.insert(0, str(LABS))
        import prepare_data
        prepare_data.main([])
    want = (DATA / "full.sha256").read_text(encoding="utf-8").strip()
    h = hashlib.sha256()
    for t in TABLES:
        h.update((FULL / f"{t}.csv").read_bytes())
    if h.hexdigest() != want:
        _say("Warning: your copy of the tables differs from the course's; reference answers may not match.")


def _load(con, folder: Path) -> None:
    con.execute(DDL)
    for t in TABLES:
        con.execute(f"INSERT INTO {t} SELECT * FROM read_csv(?, header = true, nullstr = '', auto_detect = true)",
                    [str(folder / f"{t}.csv")])


def build_db(force: bool = False) -> Path:
    ensure_data()
    if DB_FILE.exists() and not force:
        return DB_FILE
    if DB_FILE.exists():
        DB_FILE.unlink()
    _say("Building data/delivery.duckdb from the six tables...")
    con = duckdb.connect(str(DB_FILE))
    _load(con, FULL)
    con.execute(DAILY)
    con.close()
    return DB_FILE


def db(read_only: bool = True):
    """A connection to the full database. Read-only: nothing you run can change it."""
    build_db()
    return duckdb.connect(str(DB_FILE), read_only=read_only)


def mini():
    """The six tiny tables, in memory, writable: small enough to print and predict."""
    con = duckdb.connect()
    _load(con, DATA / "mini")
    return con


_DEFAULT = {"con": None}


def _con(con):
    if con is not None:
        return con
    if _DEFAULT["con"] is None:
        _DEFAULT["con"] = db()
    return _DEFAULT["con"]


def run(sql: str, con=None) -> tuple[list[str], list[tuple]]:
    """Run one query; return its column names and rows."""
    cur = _con(con).execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, (cur.fetchall() if cols else [])


def show(sql: str, con=None, n: int = 12) -> None:
    """Run a query and print the first n rows."""
    cols, data = run(sql, con)
    _print(cols, data[:n])
    if len(data) > n:
        _say(f"... {len(data)} rows in all (showing {n})")


def rows(sql: str, con=None) -> list[tuple]:
    return run(sql, con)[1]


def _fmt(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def _print(cols, data) -> None:
    table = [[str(c) for c in cols]] + [[_fmt(v) for v in r] for r in data]
    widths = [max(len(r[i]) for r in table) for i in range(len(cols))]
    for k, r in enumerate(table):
        _say("  ".join(x.ljust(w) for x, w in zip(r, widths)).rstrip())
        if k == 0:
            _say("  ".join("-" * w for w in widths))


# ------------------------------------------------------------------------------ checking answers
def _norm(v):
    if isinstance(v, decimal.Decimal):
        return round(float(v), 2)
    if isinstance(v, float):
        return round(v, 2)
    if isinstance(v, (_dt.date, _dt.datetime)):
        return v.isoformat()
    return v


def _blank(sql: str) -> bool:
    body = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    return not body.strip()


def reference(key: str) -> dict:
    return json.loads((REF / f"{key}.json").read_text(encoding="utf-8"))


def same(got: list, want: list, ordered: bool) -> tuple[bool, str]:
    if len(got) != len(want):
        return False, f"{len(got)} rows, the reference has {len(want)}"
    if got and len(got[0]) != len(want[0]):
        return False, f"{len(got[0])} columns, the reference has {len(want[0])}"
    g = [list(map(_norm, r)) for r in got]
    w = [list(r) for r in want]
    if not ordered:
        g, w = sorted(g, key=repr), sorted(w, key=repr)
    for i, (a, b) in enumerate(zip(g, w)):
        for x, y in zip(a, b):
            if isinstance(x, float) and isinstance(y, (int, float)) and abs(x - y) <= 0.011:
                continue
            if x != y:
                return False, f"first difference in row {i + 1}: {a} against {b}"
    return True, "matches the reference"


def check(key: str, sql: str, con=None, ordered: bool | None = None, quiet: bool = False):
    """Run your query, print it, compare it with the reference. Returns the rows.

    A blank query (comments only) returns the reference rows, so later cells still run.
    """
    if RECORD:
        cols, got = run(sql, con)
        data = [list(map(_norm, r)) for r in got]
        REF.mkdir(parents=True, exist_ok=True)
        rec = {"columns": cols, "rows": data, "ordered": bool(ordered) or bool(re.search(r"\border\s+by\b[^)]*$", sql, re.I | re.S))}
        (REF / f"{key}.json").write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        _say(f"recorded {key}: {len(data)} rows")
        return data
    ref = reference(key)
    if _blank(sql):
        if STRICT:
            raise AssertionError(f"{key}: the query is blank")
        _say(f"{key}: not written yet. The reference result is used so that the next cells run.")
        if not quiet:
            _print(ref["columns"], ref["rows"][:12])
        return [tuple(r) for r in ref["rows"]]
    cols, got = run(sql, con)
    if not quiet:
        _print(cols, got[:12])
        if len(got) > 12:
            _say(f"... {len(got)} rows in all")
    ok, why = same(got, ref["rows"], ref["ordered"] if ordered is None else ordered)
    _say(("PASS " if ok else "NOT YET ") + f"{key}: {why}")
    if STRICT:
        assert ok, f"{key}: {why}"
    return got


# ------------------------------------------------------------------------------ the twenty questions
def save_part(part: str, answers: dict) -> Path:
    """Write your answers of one lab to answers/<part>.sql: a prediction and a query per question."""
    ANSWERS.mkdir(exist_ok=True)
    out = [f"-- FND-DAT-101 · the twenty questions · {part}", ""]
    for key, (prediction, sql) in answers.items():
        pred = " ".join(l.strip() for l in prediction.splitlines() if l.strip() and not l.strip().startswith("--"))
        out += [f"-- name: {key}", f"-- prediction: {pred or '(none written)'}", sql.strip(), ";", ""]
    p = ANSWERS / f"{part}.sql"
    p.write_text("\n".join(out), encoding="utf-8", newline="\n")
    _say(f"saved {len(answers)} answers to answers/{p.name}")
    return p


def read_answers_text(text: str) -> dict:
    """Split a text of '-- name: key' blocks into {key: sql}."""
    found = {}
    for block in re.split(r"(?m)^-- name: ", text)[1:]:
        key, _, rest = block.partition("\n")
        sql = "\n".join(l for l in rest.splitlines() if not l.startswith("-- prediction:"))
        found[key.strip()] = sql.strip().rstrip(";").strip()
    return found


def read_answers(folder: Path = ANSWERS) -> dict:
    found = {}
    for f in sorted(folder.glob("*.sql")):
        found.update(read_answers_text(f.read_text(encoding="utf-8")))
    return found


def grade_twenty(folder: Path = ANSWERS, con=None) -> int:
    """The automatic checker: every answer file in answers/, twenty questions, 16 to pass."""
    found = read_answers(folder)
    passed = 0
    for i in range(1, 21):
        key = f"q{i:02d}"
        sql = found.get(key, "")
        if _blank(sql):
            _say(f"{key}  missing")
            continue
        try:
            got = run(sql, con)[1]
            ref = reference(key)
            ok, why = same(got, ref["rows"], ref["ordered"])
        except Exception as e:  # a query that does not run is a failed answer, not a crash
            ok, why = False, f"error: {str(e).splitlines()[0][:90]}"
        passed += ok
        _say(f"{key}  {'pass' if ok else 'fail'}  {'' if ok else why}")
    _say(f"{passed} of 20 pass (16 needed)")
    return passed


# ------------------------------------------------------------------------------ constraints
def expect_refusal(con, sql: str) -> str:
    """Run a statement that should break a constraint; print the database's message."""
    if _blank(sql):
        if STRICT:
            raise AssertionError("the statement is blank")
        _say("not written yet: write an INSERT that breaks a key or a check, then run this cell again")
        return ""
    try:
        con.execute(sql)
    except duckdb.Error as e:
        msg = str(e).splitlines()[0]
        _say("refused: " + msg)
        return msg
    _say("accepted: no constraint refused this row. Which rule did you mean to break?")
    if STRICT:
        raise AssertionError("the statement was accepted")
    return ""


# ------------------------------------------------------------------------------ the annotated schema
def _cells(line: str) -> list[str]:
    return [x.strip() for x in line.strip().strip("|").split("|")]


def check_schema(notes: str) -> int:
    """Compare an annotated schema (pipe tables) with the reference: keys and cardinalities."""
    tables, rels = {}, {}
    for line in notes.splitlines():
        if "|" not in line or set(line.strip()) <= set("|- "):
            continue
        c = _cells(line)
        if "->" in c[0] and len(c) >= 2:
            rels[c[0].replace(" ", "")] = c[1].replace(" ", "")
        elif len(c) >= 3 and c[0] not in ("table", "relationship"):
            tables[c[0]] = (frozenset(k.strip() for k in c[1].split(",") if k.strip()), c[2])
    if RECORD:
        rec = {"keys": {t: sorted(k) for t, (k, g) in tables.items()},
               "cardinality": rels}
        REF.mkdir(parents=True, exist_ok=True)
        (REF / "schema.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8", newline="\n")
        _say("recorded schema")
        return 0
    ref = json.loads((REF / "schema.json").read_text(encoding="utf-8"))
    wrong = 0
    for t, key in ref["keys"].items():
        got = tables.get(t)
        if not got or not got[0]:
            _say(f"{t:12s} key missing"); wrong += 1
        elif got[0] != frozenset(key):
            _say(f"{t:12s} key {', '.join(sorted(got[0]))}: not the reference"); wrong += 1
        elif not got[1] or "write" in got[1]:
            _say(f"{t:12s} grain not written"); wrong += 1
        else:
            _say(f"{t:12s} key and grain: ok")
    for r, card in ref["cardinality"].items():
        got = rels.get(r, "")
        ok = got == card
        wrong += not ok
        _say(f"{r:24s} {got or '?':10s} {'ok' if ok else 'not the reference'}")
    _say("annotated schema: " + ("matches the reference" if not wrong else f"{wrong} entries to revisit"))
    if STRICT:
        assert not wrong, "the annotated schema does not match"
    return wrong


# ------------------------------------------------------------------------------ workspaces
def workspace():
    """An in-memory database you can write to, with the full tables readable by their names.

    New tables go to memory; the company's database stays read-only.
    """
    build_db()
    con = duckdb.connect()
    con.execute(f"ATTACH '{DB_FILE.as_posix()}' AS shop (READ_ONLY)")
    con.execute("SET search_path = 'memory.main,shop.main'")
    return con


def mini_sqlite():
    """The mini tables in the second embedded engine, SQLite, from Python's standard library."""
    import csv
    import sqlite3

    con = sqlite3.connect(":memory:")
    for t in TABLES:
        with (DATA / "mini" / f"{t}.csv").open(encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            head = next(r)
            con.execute(f"CREATE TABLE {t} ({', '.join(head)})")
            con.executemany(f"INSERT INTO {t} VALUES ({', '.join('?' * len(head))})",
                            [[v if v != "" else None for v in row] for row in r])
    return con


# ------------------------------------------------------------------------------ predictions
def mark_predictions(predictions: str, queries: dict, con) -> int:
    """Run each query and mark the number you predicted for it."""
    pred = {}
    for line in predictions.splitlines():
        if "|" in line and not line.strip().startswith("--"):
            k, _, v = line.partition("|")
            pred[k.strip()] = v.strip()
    right = 0
    for k, sql in queries.items():
        got = run(sql, con)[1][0][0]
        p = pred.get(k, "")
        ok = p != "" and p.replace(".", "", 1).lstrip("-").isdigit() and abs(float(p) - float(got)) < 1e-9
        right += ok
        _say(f"{k}  predicted {p or '?':>4}  got {_fmt(got):>4}  {'right' if ok else 'missed' if p else 'no prediction'}")
    _say(f"{right} of {len(queries)} predicted right")
    if STRICT:
        assert right == len(queries), "a prediction of the solution is wrong"
    return right


# ------------------------------------------------------------------------------ the window drills
def grade_windows(folder: Path = ANSWERS, con=None) -> int:
    """The window checker: six drills, each matching its reference and explaining its partition."""
    found = read_answers(folder)
    passed = 0
    for i in range(1, 7):
        key = f"w{i}"
        sql = found.get(key, "")
        if _blank(sql):
            _say(f"{key}  missing")
            continue
        try:
            ref = reference(key)
            ok, why = same(run(sql, con)[1], ref["rows"], ref["ordered"])
        except Exception as e:
            ok, why = False, f"error: {str(e).splitlines()[0][:90]}"
        explained = bool(re.search(r"--[^\n]*partition", sql, re.I))
        if ok and not explained:
            ok, why = False, "the result matches, but no comment explains the partition (-- partition: ...)"
        passed += ok
        _say(f"{key}  {'pass' if ok else 'fail'}  {'' if ok else why}")
    _say(f"{passed} of 6 drills pass")
    if STRICT:  # a drill file missing because its lab was not run here is not a failure of this lab
        present = sum(1 for i in range(1, 7) if not _blank(found.get(f"w{i}", "")))
        assert passed == present, "a window drill of the solution fails"
    return passed


# ------------------------------------------------------------------------------ Day 4: loading
EXTRACTS = DATA / "extracts"
JULY = DATA / "july"


def _probe(con, sql) -> bool:
    try:
        con.execute(sql)
        return True
    except duckdb.Error:
        return False


def check_definitions(ddl: str) -> int:
    """Run your definition script in an empty database and try good and bad rows against it."""
    if _blank(ddl):
        if STRICT:
            raise AssertionError("the definition script is blank")
        _say("not written yet: write the three CREATE TABLE statements, then run this cell again")
        return 0
    con = duckdb.connect()
    con.execute(ddl)
    probes = [
        ("a valid customer is accepted", True, "INSERT INTO customers VALUES ('C1','2026-07-01','North','n','p','e',1990,true)"),
        ("a second customer with the same key is refused", False, "INSERT INTO customers VALUES ('C1','2026-07-02','South','n','p','e',1990,true)"),
        ("a customer without a key is refused", False, "INSERT INTO customers VALUES (NULL,'2026-07-01','North','n','p','e',1990,true)"),
        ("a region outside the five is refused", False, "INSERT INTO customers VALUES ('C2','2026-07-01','Nrth','n','p','e',1990,true)"),
        ("a valid order is accepted", True, "INSERT INTO orders VALUES ('O1','C1','S01','2026-07-01 10:00:00','delivered',9.00)"),
        ("an order of an unknown customer is refused", False, "INSERT INTO orders VALUES ('O2','C9','S01','2026-07-01 10:00:00','delivered',9.00)"),
        ("an order with an unknown status is refused", False, "INSERT INTO orders VALUES ('O3','C1','S01','2026-07-01 10:00:00','deliverd',9.00)"),
        ("a valid line is accepted", True, "INSERT INTO order_lines VALUES ('O1',1,'P0001',2,6.50,NULL,'ok')"),
        ("a second line with the same order and line number is refused", False, "INSERT INTO order_lines VALUES ('O1',1,'P0002',1,4.00,NULL,'ok')"),
        ("a line of an unknown order is refused", False, "INSERT INTO order_lines VALUES ('O9',1,'P0001',1,4.00,NULL,'ok')"),
        ("a quantity of 0 is refused", False, "INSERT INTO order_lines VALUES ('O1',2,'P0001',0,4.00,NULL,'ok')"),
    ]
    good = 0
    for label, accept, sql in probes:
        ok = _probe(con, sql) == accept
        good += ok
        _say(f"{'ok  ' if ok else 'MISS'} {label}")
    _say(f"definition script: {good} of {len(probes)} probes behave as the rules say")
    ANSWERS.mkdir(exist_ok=True)
    (ANSWERS / "july_schema.sql").write_text(ddl.strip() + "\n", encoding="utf-8", newline="\n")
    if STRICT:
        assert good == len(probes), "the definition script lets a bad row in or refuses a good one"
    return good


def stage_extracts(con) -> None:
    """Load the three raw extracts as text, numbered in file order: stg_customers, stg_orders, stg_order_lines."""
    for t in ["customers", "orders", "order_lines"]:
        con.execute(f"""CREATE OR REPLACE TABLE stg_{t} AS
            SELECT ROW_NUMBER() OVER () AS row_no, *
            FROM read_csv(?, header = true, all_varchar = true)""", [str(EXTRACTS / f"{t}_raw.csv")])
        n = con.execute(f"SELECT COUNT(*) FROM stg_{t}").fetchone()[0]
        _say(f"stg_{t}: {n} rows read")


KEYS = {"customers": "customer_id", "orders": "order_id", "order_lines": "order_id, line_no"}


def july_workspace(ddl: str):
    """An empty database in memory with your definitions, and the three extracts staged as text."""
    con = duckdb.connect()
    if _blank(ddl):
        _say("no definitions yet: the tables are missing, so the inserts below will fail and roll back")
    else:
        con.execute(ddl)
    stage_extracts(con)
    return con


def rejects(con, table: str, sql: str) -> None:
    """Keep the staged rows your rule gives a reason as rej_<table>; the others become the view ok_<table>."""
    if _blank(sql):
        if STRICT:
            raise AssertionError(f"the reject rule for {table} is blank")
        _say(f"rule for {table} not written yet: no row is rejected, so the insert may fail and roll back")
        con.execute(f"CREATE OR REPLACE TABLE rej_{table} AS SELECT row_no, NULL::VARCHAR AS reason FROM stg_{table} WHERE false")
    else:
        con.execute(f"CREATE OR REPLACE TABLE rej_{table} AS SELECT * FROM (\n{sql.strip().rstrip(';')}\n) WHERE reason IS NOT NULL")
    con.execute(f"CREATE OR REPLACE VIEW ok_{table} AS SELECT * FROM stg_{table} WHERE row_no NOT IN (SELECT row_no FROM rej_{table})")
    for reason, n in con.execute(f"SELECT reason, COUNT(*) FROM rej_{table} GROUP BY reason ORDER BY reason").fetchall():
        _say(f"rej_{table}: {n:3d} {reason}")
    left = con.execute(f"SELECT COUNT(*) FROM ok_{table}").fetchone()[0]
    _say(f"ok_{table}: {left} rows left to insert")


def in_transaction(con, sql: str) -> bool:
    """Run your statements between BEGIN and COMMIT; if one fails, roll everything back."""
    if _blank(sql):
        if STRICT:
            raise AssertionError("the inserts are blank")
        _say("not written yet: nothing inserted")
        return False
    con.execute("BEGIN TRANSACTION")
    try:
        con.execute(sql)
        con.execute("COMMIT")
        _say("committed")
        return True
    except duckdb.Error as e:
        con.execute("ROLLBACK")
        _say("rolled back, nothing kept: " + str(e).splitlines()[0][:160])
        if STRICT:
            raise
        return False


def _count(con, table: str) -> int:
    try:
        return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except duckdb.Error:
        return 0


def load_log(con) -> list:
    """Count read, loaded and rejected rows per table and reason; write answers/load_log.csv; compare."""
    rows = []
    for t in ["customers", "orders", "order_lines"]:
        read = _count(con, f"stg_{t}")
        loaded = _count(con, t)
        rows.append([t, "loaded", loaded])
        for reason, n in con.execute(f"SELECT reason, COUNT(*) FROM rej_{t} GROUP BY reason ORDER BY reason").fetchall():
            rows.append([t, reason, n])
        rejected = sum(r[2] for r in rows if r[0] == t and r[1] != "loaded")
        _say(f"{t:12s} read {read:5d} = loaded {loaded:5d} + rejected {rejected:3d}  {'accounted' if read == loaded + rejected else 'NOT ACCOUNTED'}")
    for r in rows:
        if r[1] != "loaded":
            _say(f"   {r[0]:12s} {r[1]:18s} {r[2]:4d}")
    ANSWERS.mkdir(exist_ok=True)
    with (ANSWERS / "load_log.csv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("table,outcome,rows\n" + "".join(f"{a},{b},{c}\n" for a, b, c in rows))
    ref = json.loads((REF / "load_log.json").read_text(encoding="utf-8"))
    ok = sorted(map(tuple, rows)) == sorted(map(tuple, ref["rows"]))
    _say("load log: " + ("matches the expected log" if ok else "differs from the expected log"))
    if STRICT:
        assert ok, "the load log differs from the expected log"
    return rows


def july_db():
    """The July tables as a correct load leaves them (data/july/), in memory, writable."""
    con = duckdb.connect()
    money = {"orders": ", types = {'delivery_fee': 'DECIMAL(10,2)'}",
             "order_lines": ", types = {'unit_price': 'DECIMAL(10,2)', 'discount': 'DECIMAL(10,2)'}"}
    for t in ["stores", "customers", "orders", "order_lines"]:
        types = money.get(t, "")
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv(?, header = true, nullstr = ''{types})", [str(JULY / f"{t}.csv")])
    return con


def test_view(con, view: str, banned=("full_name", "phone", "email", "birth_year", "joined_on", "marketing_opt_in")) -> bool:
    """The view exists, and none of the columns the analysts do not need appear in it."""
    try:
        cols = view_columns(con, view)
    except duckdb.Error:
        if STRICT:
            raise AssertionError(f"the view {view} does not exist")
        _say(f"{view}: not created yet")
        return False
    found = [c for c in cols if c.lower() in banned]
    _say(f"{view} columns: {', '.join(cols)}")
    _say("PASS no name, phone, e-mail, exact birth year, join date or opt-in" if not found
         else "NOT YET these columns should not be in the view: " + ", ".join(found))
    if STRICT:
        assert not found, f"{view} exposes {found}"
    return not found


# ------------------------------------------------------------------------------ Day 4: labels and views
def _pairs(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if "|" in line and not line.strip().startswith("--"):
            k, _, v = line.partition("|")
            out[k.strip().lower()] = v.strip().lower()
    return out


def check_pairs(key: str, text: str) -> int:
    """Compare a 'name | answer' table with the reference."""
    got = _pairs(text)
    if RECORD:
        REF.mkdir(parents=True, exist_ok=True)
        (REF / f"{key}.json").write_text(json.dumps(got, indent=1) + "\n", encoding="utf-8", newline="\n")
        _say(f"recorded {key}")
        return 0
    ref = json.loads((REF / f"{key}.json").read_text(encoding="utf-8"))
    wrong = 0
    for k, v in ref.items():
        g = got.get(k, "")
        ok = g.split(";")[0].strip().split(",")[0].strip() == v.split(";")[0].strip().split(",")[0].strip()
        wrong += not ok
        _say(f"{k:18s} {g.split(';')[0][:28] or '?':28s} {'ok' if ok else 'revisit'}")
    _say(f"{key}: {len(ref) - wrong} of {len(ref)} agree with the reference")
    if STRICT:
        assert not wrong, f"{key} differs from the reference"
    return wrong


def view_columns(con, view: str) -> list[str]:
    return [r[0] for r in con.execute(f"DESCRIBE {view}").fetchall()]


# ------------------------------------------------------------------------------ Day 4: plans
def sqlite_orders():
    """The orders table in SQLite (standard library), in memory, without any index."""
    import csv
    import sqlite3

    ensure_data()
    con = sqlite3.connect(":memory:")
    with (FULL / "orders.csv").open(encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        head = next(r)
        con.execute(f"CREATE TABLE orders ({', '.join(head)})")
        marks = ", ".join("?" for _ in head)
        con.executemany(f"INSERT INTO orders VALUES ({marks})", r)
    return con


def plan_sqlite(con, sql: str) -> str:
    """EXPLAIN QUERY PLAN in SQLite: the detail lines, such as SCAN orders."""
    if _blank(sql):
        _say("not written yet")
        return ""
    lines = [row[-1] for row in con.execute(sql).fetchall()]
    for line in lines:
        _say(line)
    return "\n".join(lines)


def expect_plan(plan: str, word: str, what: str) -> bool:
    """Does the plan contain the operator word (SCAN, SEARCH, ...)?"""
    if not plan:
        _say(f"{what}: no plan yet")
        if STRICT:
            raise AssertionError(f"{what}: no plan")
        return False
    ok = any(line.strip().upper().startswith(word.upper()) for line in plan.splitlines())
    _say(("PASS " if ok else "NOT YET ") + f"{what}: the plan {'shows' if ok else 'does not show'} {word}")
    if STRICT:
        assert ok, what
    return ok


def plan_duckdb(sql: str, con=None) -> str:
    if _blank(sql):
        _say("not written yet")
        return ""
    text = "\n".join(r[1] for r in run(sql, con)[1])
    _say(text)
    return text


# ------------------------------------------------------------------------------ Day 4: tests of generated queries
VERIFY = DATA / "verification"


def generated_queries() -> dict:
    return read_answers(VERIFY)


def _eq(x: str, y: str) -> bool:
    try:
        return abs(float(x) - float(y)) < 0.006
    except ValueError:
        return x.strip().lower() == y.strip().lower()


def run_tests(expected: str, con, queries: dict | None = None) -> dict:
    """Run each generated query on the mini tables and compare with your hand-checked answer."""
    want = _pairs(expected)
    results = {}
    for key, sql in (queries if queries is not None else generated_queries()).items():
        got_rows = run(sql, con)[1]
        got = ", ".join(_fmt(v) for v in got_rows[0]) if got_rows else "(no row)"
        exp = want.get(key, "")
        if not exp:
            verdict = "no expected answer"
        else:
            a = [x.strip() for x in got.split(",")]
            b = [x.strip() for x in exp.split(",")]
            verdict = "pass" if len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b)) else "FAIL"
        results[key] = (exp, got, verdict)
        _say(f"{key}  expected {exp or '?':16s} got {got:16s} {verdict}")
    return results


def write_note(results: dict, verdicts: str) -> Path:
    """Write answers/verification_note.md: each query, the test result and your judgement."""
    judge = _pairs(verdicts)
    lines = ["# Verification note: ten generated queries", "",
             "| Query | Expected (by hand) | Got | Test | Judgement |", "|---|---|---|---|---|"]
    for k, (exp, got, verdict) in results.items():
        lines.append(f"| {k} | {exp} | {got} | {verdict} | {judge.get(k, '')} |")
    ANSWERS.mkdir(exist_ok=True)
    p = ANSWERS / "verification_note.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    _say(f"wrote answers/{p.name}")
    return p
