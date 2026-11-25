"""One test per question: the query on the fixture against the rows you worked out by hand.

    uv run pytest capstone/tests -q          # from labs/

A question is skipped, not failed, while its query is blank or its expected file
(tests/expected/qNN.csv) is missing. Write the expected file by hand: the header is the
query's column names, then one line per row. Rows are compared in any order; numbers are
compared to two decimals; an empty cell means NULL.
"""
from __future__ import annotations

import csv
import sys
from decimal import Decimal
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cap  # noqa: E402

EXPECTED = HERE / "expected"
KEYS = [f"q{i:02d}" for i in range(1, 11)]


@pytest.fixture(scope="module")
def con():
    return cap.connect(cap.FIXTURE)


def norm(v) -> str:
    if v is None or v == "":
        return ""
    try:
        return f"{Decimal(str(v)):.2f}"
    except ArithmeticError:
        return str(v).strip().lower()


@pytest.mark.parametrize("key", KEYS)
def test_query(key, con):
    if cap.is_blank(cap.query_text(key)):
        pytest.skip(f"{key}: the query is not written yet")
    path = EXPECTED / f"{key}.csv"
    if not path.exists():
        pytest.skip(f"{key}: write tests/expected/{key}.csv by hand first")
    with path.open(encoding="utf-8", newline="") as f:
        table = list(csv.reader(f))
    want_cols, want = table[0], table[1:]
    cols, got = cap.run(key, con)
    assert [c.lower() for c in cols] == [c.strip().lower() for c in want_cols], f"{key}: columns {cols}, expected {want_cols}"
    assert sorted([norm(v) for v in r] for r in got) == sorted([norm(v) for v in r] for r in want)
