"""Write the synthetic business orders data of the capstone (July to December 2026).

    uv run python capstone/prepare_capstone.py      # from labs/: writes capstone/data/full/*.csv

Deterministic: the same seed writes the same files on every computer (random.random() only).
Everything is synthetic. Accounts are organisations named only by a code and a segment; their
contact person appears as "Synthetic Contact 0001" with a phone and an e-mail that are invalid
on purpose (TEL-A0001-X, a0001@example.invalid).
"""
from __future__ import annotations

import csv
import hashlib
import random
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "full"
SEED = 2026_07
REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["office", "school", "clinic", "restaurant"]
CATEGORIES = {
    "Paper": ["Copy paper A4, box of 5 reams", "Paper towels, case of 12", "Toilet tissue, case of 48", "Napkins, pack of 500"],
    "Cleaning": ["Floor cleaner 5 L", "Hand soap 5 L", "Disinfectant spray, case of 12", "Bin liners, roll of 50", "Dish detergent 5 L"],
    "Kitchen": ["Paper cups, sleeve of 50", "Wooden stirrers, box of 1000", "Food containers, pack of 100", "Aluminium foil 30 cm"],
    "First aid": ["Plasters, box of 100", "Gauze pads, pack of 50", "Disposable gloves, box of 100", "Face masks, box of 50"],
    "Stationery": ["Ballpoint pens, box of 50", "Staples, box of 5000", "Folders, pack of 25", "Sticky notes, pack of 12"],
    "Beverages": ["Bottled water 330 ml, case of 40", "Tea bags, box of 100", "Ground coffee 1 kg", "Sugar sticks, box of 1000"],
}
START, END = date(2026, 7, 1), date(2026, 12, 31)


class Rng:
    def __init__(self, seed: int):
        self.r = random.Random(seed)

    def u(self) -> float:
        return self.r.random()

    def int(self, lo: int, hi: int) -> int:
        return lo + min(int(self.u() * (hi - lo + 1)), hi - lo)

    def pick(self, seq):
        return seq[self.int(0, len(seq) - 1)]

    def weighted(self, items, weights):
        x, acc = self.u() * sum(weights), 0.0
        for it, w in zip(items, weights):
            acc += w
            if x < acc:
                return it
        return items[-1]


def money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def tables(rng: Rng) -> dict:
    # accounts
    accounts = []
    for i in range(1, 601):
        seg = rng.weighted(SEGMENTS, [45, 20, 15, 20])
        opened = date(2024, 1, 1) + timedelta(days=rng.int(0, 900))
        accounts.append([f"A{i:04d}", seg, rng.pick(REGIONS), opened.isoformat(), f"Synthetic Contact {i:04d}",
                         f"TEL-A{i:04d}-X", f"a{i:04d}@example.invalid", rng.pick(["15000.00", "25000.00", "40000.00", "80000.00"])])
    # delivery sites: most in the account's region, some elsewhere
    sites, by_account = [], {}
    s_n = 0
    for a in accounts:
        for _ in range(rng.weighted([1, 2, 3, 4], [50, 30, 15, 5])):
            s_n += 1
            region = a[2] if rng.u() < 0.7 else rng.pick(REGIONS)
            sid = f"ST{s_n:04d}"
            sites.append([sid, a[0], region, "true" if rng.u() < 0.95 else "false"])
            by_account.setdefault(a[0], []).append(sid)
    # items and the price list (valid_to is exclusive; empty means still valid)
    items, prices = [], []
    i_n = 0
    for cat, bases in CATEGORIES.items():
        for base in bases:
            for grade in ["standard", "premium"]:
                i_n += 1
                iid = f"I{i_n:04d}"
                items.append([iid, f"{base}, {grade}", cat, "true" if rng.u() < 0.92 else "false"])
                cents = rng.int(800, 9000) * (2 if grade == "premium" else 1)
                start = date(2026, 1, 1)
                changes = sorted({START + timedelta(days=rng.int(10, 170)) for _ in range(rng.weighted([0, 1, 2], [45, 40, 15]))})
                for ch in changes:
                    prices.append([iid, start.isoformat(), ch.isoformat(), money(cents)])
                    cents = int(cents * (1 + rng.int(3, 12) / 100))
                    start = ch
                prices.append([iid, start.isoformat(), "", money(cents)])
    # never ordered: the last item of every category
    never = {items[k][0] for k in range(len(items)) if (k + 1) % 8 == 0}
    orderable = [it for it in items if it[3] == "true" and it[0] not in never]
    # orders, lines, shipments
    silent = {a[0] for a in accounts if rng.u() < 0.1}          # accounts that never order
    active = [a for a in accounts if a[0] not in silent]
    orders, lines, ships = [], [], []
    sh_n = 0
    for o in range(1, 10001):
        a = rng.pick(active)
        ordered = START + timedelta(days=rng.int(0, (END - START).days))
        days_left = (END - ordered).days
        status = rng.weighted(["closed", "open", "cancelled"], [85, 10, 5]) if days_left > 14 else rng.weighted(["closed", "open", "cancelled"], [40, 55, 5])
        oid = f"B{o:06d}"
        orders.append([oid, a[0], rng.pick(by_account[a[0]]), ordered.isoformat(), status])
        short = status == "closed" and rng.u() < 0.06          # closed without shipping everything
        for ln in range(1, rng.weighted([1, 2, 3, 4, 5, 6], [10, 20, 25, 20, 15, 10]) + 1):
            it = rng.pick(orderable)
            qty = rng.int(1, 40)
            lines.append([oid, ln, it[0], qty])
            if status == "cancelled":
                continue
            if status == "closed":
                to_ship = qty if not short or ln > 1 else max(0, qty - rng.int(1, qty))
            else:
                to_ship = rng.weighted([0, qty // 2, qty], [50, 30, 20])
            parts = 1 if to_ship < 4 else rng.weighted([1, 2, 3], [75, 18, 7])
            day = ordered + timedelta(days=rng.int(0, 3))
            left = to_ship
            for p in range(parts):
                q = left if p == parts - 1 else rng.int(1, left - (parts - p - 1))
                left -= q
                if q <= 0:
                    continue
                sh_n += 1
                ships.append([f"SH{sh_n:06d}", oid, ln, day.isoformat(), q,
                              "returned" if rng.u() < 0.03 else "delivered"])
                day += timedelta(days=rng.int(1, 6))
    return {
        "accounts": (["account_id", "segment", "region", "opened_on", "contact_name", "contact_phone", "contact_email", "credit_limit"], accounts),
        "sites": (["site_id", "account_id", "region", "is_active"], sites),
        "items": (["item_id", "item_name", "category", "is_active"], items),
        "price_list": (["item_id", "valid_from", "valid_to", "unit_price"], prices),
        "bulk_orders": (["order_id", "account_id", "site_id", "ordered_on", "status"], orders),
        "bulk_lines": (["order_id", "line_no", "item_id", "qty_ordered"], lines),
        "shipments": (["shipment_id", "order_id", "line_no", "shipped_on", "qty_shipped", "outcome"], ships),
    }


def main(argv) -> int:
    digest = hashlib.sha256()
    for name, (header, rows) in tables(Rng(SEED)).items():
        p = OUT / f"{name}.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)
        digest.update(p.read_bytes())
        print(f"{name:12s} {len(rows):>7,} rows")
    print("sha256", digest.hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
