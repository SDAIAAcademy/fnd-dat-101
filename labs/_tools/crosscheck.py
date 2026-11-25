"""Compare the recorded references with the numbers prepare_data.py computed in plain Python.

    uv run python _tools/crosscheck.py      # from labs/, after run_all.py --record

The references are recorded from the solution queries; this script is the independent check
that those queries say what the data generator planted.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
REF = LABS / "data" / "reference"
key = json.loads((LABS / "solutions" / "key_numbers.json").read_text(encoding="utf-8"))
fails = 0


def ref(name):
    p = REF / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8"))["rows"] if p.exists() else None


def same(label, got, want):
    global fails
    ok = abs(float(got) - float(want)) < 0.006 if isinstance(want, (int, float, str)) and str(want).replace(".", "", 1).lstrip("-").isdigit() else got == want
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {label}: reference {got}, generator {want}")


checks = []
if (r := ref("l11_orders")): same("orders", r[0][0], key["rows"]["orders"])
if (r := ref("l11_lines_key")): same("order lines", r[0][0], key["rows"]["order_lines"])
if (r := ref("l12_attempts_max")): same("most attempts", r[0][0], key["max_attempts"])
if (r := ref("l12_orders_without_attempt")): same("orders without attempt = cancelled", r[0][0], key["orders_by_status"]["cancelled"])
if (r := ref("l13_wide_rows")): same("wide rows = order lines", r[0][0], key["rows"]["order_lines"])
if (r := ref("q13")):
    same("customers never ordered", sum(x[2] for x in r), key["customers_never_ordered"])
    same("customers without region", [x for x in r if x[0] == "none"][0][1], key["customers_without_region"])
if (r := ref("q14")): same("active products never sold", len(r), 20)
if (r := ref("l31_fanout")):
    same("true sum of line value", r[0][1], key["sum_qty_times_price_all_lines"])
    same("sum after joining attempts", r[0][0], key["sum_after_joining_deliveries"])
if (r := ref("q19")):
    for month, value in r:
        same(f"net revenue {month[:7]}", value, key["net_revenue_by_delivery_month"][month[:7]])
if (r := ref("l22_no_discount")) is not None:
    pass
print("crosscheck:", "all agree" if not fails else f"{fails} disagree")
sys.exit(1 if fails else 0)
