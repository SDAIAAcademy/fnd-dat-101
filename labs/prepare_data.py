# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write the synthetic data of the grocery delivery company (FND-DAT-101).

    uv run prepare_data.py            # from labs/: the full tables, about 20 seconds
    uv run prepare_data.py --small    # the committed files only (mini tables and extracts)

Python standard library only, seed 101, the same bytes on every run and every machine: only
random.random() is used, which Python documents as reproducible for a given seed.

Writes
  data/full/*.csv       six tables, January to June 2026, about a million order lines (git ignores them)
  data/full.sha256      the digest of those files, committed, so a participant's copy can be checked
  data/mini/*.csv       six tiny tables to print and predict from (committed)
  data/extracts/*.csv   three raw July extracts with seeded defects for Day 4 (committed)
  solutions/key_numbers.json   numbers computed here, in Python, without SQL: the trainer's key

Everything is synthetic. People are codes. Names, phone numbers and e-mail addresses are
tokens that cannot be dialled or mailed: phones start with letters, e-mail addresses use the
reserved domain example.invalid.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
SEED = 101
START = date(2026, 1, 1)
DAYS = 181                      # 1 January to 30 June 2026
REGIONS = ["North", "South", "East", "West", "Central"]
STORES = [  # store_id, region, opened_on, area_m2
    ("S01", "North", date(2024, 3, 1), 820), ("S02", "North", date(2024, 9, 15), 640),
    ("S03", "South", date(2023, 11, 1), 910), ("S04", "East", date(2024, 1, 20), 700),
    ("S05", "West", date(2024, 6, 1), 760), ("S06", "Central", date(2023, 5, 10), 1050),
    ("S07", "Central", date(2025, 2, 1), 580), ("S08", "South", date(2026, 4, 1), 690),
]
S05_CLOSED = {date(2026, 3, 10), date(2026, 3, 11), date(2026, 3, 12)}   # planted: closed days
CATEGORIES = {
    "Produce": (["Tomatoes", "Cucumbers", "Onions", "Potatoes", "Bananas", "Apples", "Oranges", "Lemons", "Carrots", "Lettuce", "Grapes", "Mint"], ["500 g", "1 kg", "2 kg", "bunch"], (300, 1800)),
    "Dairy": (["Fresh milk", "Laban", "Yoghurt", "White cheese", "Butter", "Cream", "Labneh", "Eggs"], ["500 ml", "1 L", "2 L", "pack of 12", "400 g"], (350, 2600)),
    "Bakery": (["White bread", "Brown bread", "Flat bread", "Croissants", "Sesame rings", "Date rolls"], ["pack of 4", "pack of 6", "loaf"], (200, 1500)),
    "Pantry": (["Rice", "Lentils", "Pasta", "Flour", "Sugar", "Tea", "Coffee", "Dates", "Olive oil", "Honey", "Tahini", "Chickpeas"], ["500 g", "1 kg", "2 kg", "5 kg", "1 L"], (500, 6500)),
    "Beverages": (["Water", "Orange juice", "Mango juice", "Sparkling water", "Iced tea"], ["330 ml", "1 L", "1.5 L", "pack of 12"], (150, 3500)),
    "Frozen": (["Frozen peas", "Frozen chicken", "Ice cream", "Frozen fish", "Frozen fries"], ["400 g", "1 kg", "2 kg"], (900, 5500)),
    "Household": (["Dish soap", "Laundry powder", "Tissues", "Bin bags", "Kitchen towels", "Floor cleaner"], ["500 ml", "1 L", "3 kg", "pack of 10"], (600, 4500)),
    "Personal care": (["Shampoo", "Hand soap", "Toothpaste", "Body lotion", "Cotton pads"], ["200 ml", "400 ml", "pack of 3"], (700, 3800)),
}
N_PRODUCTS, N_CUSTOMERS, N_ORDERS = 1200, 40000, 250000
WEEKDAY_WEIGHT = [1.0, 0.95, 1.0, 1.25, 1.35, 1.1, 0.95]  # Monday .. Sunday


LIQUID = {"Fresh milk", "Laban", "Cream", "Olive oil", "Water", "Orange juice", "Mango juice", "Sparkling water",
          "Iced tea", "Dish soap", "Floor cleaner", "Shampoo", "Hand soap", "Body lotion"}
PACKED = {"Eggs", "White bread", "Brown bread", "Flat bread", "Croissants", "Sesame rings", "Date rolls",
          "Tissues", "Bin bags", "Kitchen towels", "Cotton pads"}


def size_for(noun: str, sizes: list[str]) -> list[str]:
    """Sizes that suit the product: volumes for liquids, packs for packed goods, weights for the rest."""
    if noun in LIQUID:
        return ["330 ml", "500 ml", "1 L", "1.5 L", "2 L"]
    if noun in PACKED:
        return ["pack of 4", "pack of 6", "pack of 12"]
    if noun in ("Mint", "Lettuce"):
        return ["bunch"]
    return ["250 g", "500 g", "1 kg", "2 kg", "5 kg"]


def money(h: int) -> str:
    return f"{h // 100}.{h % 100:02d}" if h >= 0 else "-" + money(-h)


class Rng:
    """random.random() only, so the stream is the same on every Python version."""

    def __init__(self, seed: int):
        self.r = random.Random(seed)

    def u(self) -> float:
        return self.r.random()

    def int(self, lo: int, hi: int) -> int:          # inclusive
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


def write_csv(path: Path, header, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------------------- the full tables
def full_tables(rng: Rng):
    stores = [(s, r, o.isoformat(), a) for s, r, o, a in STORES]
    store_by_region = {r: [s for s, rr, o, a in STORES if rr == r] for r in REGIONS}

    products, prices = [], {}
    cats = list(CATEGORIES)
    for i in range(1, N_PRODUCTS + 1):
        cat = cats[(i - 1) % len(cats)]
        nouns, sizes, (lo, hi) = CATEGORIES[cat]
        noun = rng.pick(nouns)
        name = f"{noun} {rng.pick(size_for(noun, sizes))}"
        price = rng.int(lo // 5, hi // 5) * 5
        pid = f"P{i:04d}"
        prices[pid] = price
        category = "" if i % 100 == 37 else cat          # planted: 12 products without a category
        products.append([pid, name, category, money(price), "true"])
    unsold = {f"P{i:04d}" for i in range(1161, 1201)}     # planted: 40 products never sold
    for p in products:
        if p[0] in unsold and p[0] < "P1181":              # 20 of them withdrawn, 20 still listed as active
            p[4] = "false"
    sellable = [p[0] for p in products if p[0] not in unsold]
    pop = [1.0 / (1 + (k % 97) * 0.15) for k in range(len(sellable))]   # some products sell far more

    customers, cust_region = [], {}
    for i in range(1, N_CUSTOMERS + 1):
        cid = f"C{i:05d}"
        region = "" if rng.u() < 0.03 else rng.pick(REGIONS)      # planted: about 3% without a region
        joined = date(2025, 1, 1) + timedelta(days=rng.int(0, 545))
        customers.append([cid, joined.isoformat(), region, f"Synthetic Person {i:05d}",
                          f"TEL-{i:05d}-X", f"c{i:05d}@example.invalid", rng.int(1950, 2006),
                          "true" if rng.u() < 0.4 else "false"])
        cust_region[cid] = (region, joined)
    buyers = [c[0] for c in customers if rng.u() < 0.85]          # planted: about 15% never order
    buyer_w = [1.0 / (1 + (k % 50) * 0.2) for k in range(len(buyers))]

    days = [START + timedelta(days=d) for d in range(DAYS)]
    day_w = [WEEKDAY_WEIGHT[d.weekday()] for d in days]
    cum_b, acc = [], 0.0
    for w in buyer_w:
        acc += w
        cum_b.append(acc)
    cum_p, acc = [], 0.0
    for w in pop:
        acc += w
        cum_p.append(acc)
    cum_d, acc = [], 0.0
    for w in day_w:
        acc += w
        cum_d.append(acc)

    def draw(cum, items):
        x = rng.u() * cum[-1]
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid] > x:
                hi = mid
            else:
                lo = mid + 1
        return items[lo]

    orders, lines, deliveries = [], [], []
    couriers = {s: [f"K{j:03d}" for j in range(1 + 15 * k, 16 + 15 * k)] for k, (s, *_ ) in enumerate(STORES)}
    oid_n = 0
    while len(orders) < N_ORDERS:
        cid = draw(cum_b, buyers)
        region, joined = cust_region[cid]
        d = draw(cum_d, days)
        if d < joined:
            continue
        store = rng.pick(store_by_region[region]) if region else rng.pick([s[0] for s in STORES])
        if store == "S08" and d < date(2026, 4, 1):
            store = "S03"
        if store == "S05" and d in S05_CLOSED:
            continue
        oid_n += 1
        oid = f"O{oid_n:07d}"
        at = datetime(d.year, d.month, d.day) + timedelta(minutes=rng.int(7 * 60, 23 * 60 + 30))
        x = rng.u()
        status = "cancelled" if x < 0.05 else ("returned" if x < 0.08 else "delivered")
        n_lines = 1 + int(rng.u() * 4) + int(rng.u() * 4)       # 1 to 7, mean 4
        basket = 0
        for ln in range(1, n_lines + 1):
            pid = draw(cum_p, sellable)
            qty = 1 + int(rng.u() * rng.u() * 5)
            price = prices[pid]
            if rng.u() < 0.08:                                    # a promotion price on some lines
                price = price * 9 // 10
            y = rng.u()
            if y < 0.75:
                disc = ""                                         # planted: NULL means no discount
            elif y < 0.80:
                disc = "0.00"
            else:
                disc = money(qty * price * rng.int(5, 20) // 100)
            lstat = "cancelled" if rng.u() < 0.02 else "ok"
            lines.append([oid, ln, pid, qty, money(price), disc, lstat])
            if lstat == "ok":
                basket += qty * price - (0 if disc in ("", "0.00") else int(round(float(disc) * 100)))
        fee = 0 if basket >= 10000 else 900
        orders.append([oid, cid, store, at.strftime("%Y-%m-%d %H:%M:%S"), status, money(fee)])
        if status != "cancelled":                                 # planted: cancelled orders have no attempt
            t = at + timedelta(minutes=rng.int(40, 300))
            attempt = 1
            while True:
                failed = rng.u() < (0.07 if attempt == 1 else 0.15) and attempt < 3
                deliveries.append([f"D{len(deliveries) + 1:07d}", oid, attempt, rng.pick(couriers[store]),
                                   t.strftime("%Y-%m-%d %H:%M:%S"), "failed" if failed else "delivered"])
                if not failed:
                    break
                attempt += 1
                t = t + timedelta(hours=rng.int(18, 30))
    return {
        "stores": (["store_id", "region", "opened_on", "area_m2"], stores),
        "products": (["product_id", "product_name", "category", "list_price", "is_active"], products),
        "customers": (["customer_id", "joined_on", "region", "full_name", "phone", "email", "birth_year", "marketing_opt_in"], customers),
        "orders": (["order_id", "customer_id", "store_id", "ordered_at", "status", "delivery_fee"], orders),
        "order_lines": (["order_id", "line_no", "product_id", "quantity", "unit_price", "discount", "line_status"], lines),
        "deliveries": (["delivery_id", "order_id", "attempt_no", "courier_id", "attempted_at", "outcome"], deliveries),
    }


def key_numbers(t) -> dict:
    """The trainer's key, computed in Python from the rows, never with SQL."""
    orders, lines, dels = t["orders"][1], t["order_lines"][1], t["deliveries"][1]
    status = {o[0]: o[4] for o in orders}
    delivered_on = {}
    for d in dels:
        if d[5] == "delivered":
            delivered_on[d[1]] = d[4][:10]
    attempts = {}
    for d in dels:
        attempts[d[1]] = attempts.get(d[1], 0) + 1
    h = lambda s: int(round(float(s) * 100)) if s else 0
    net, net_by_month_delivery, gross_naive, fanout = 0, {}, 0, 0
    for o_id, ln, pid, q, price, disc, ls in lines:
        value = q * h(price)
        gross_naive += value
        fanout += value * attempts.get(o_id, 0)          # an inner join drops orders without an attempt
        if status[o_id] == "delivered" and ls == "ok":
            v = value - h(disc)
            net += v
            m = delivered_on[o_id][:7]
            net_by_month_delivery[m] = net_by_month_delivery.get(m, 0) + v
    cust_ids = {c[0] for c in t["customers"][1]}
    buyers = {o[1] for o in orders}
    sold = {l[2] for l in lines}
    return {
        "rows": {k: len(v[1]) for k, v in t.items()},
        "orders_by_status": {s: sum(1 for o in orders if o[4] == s) for s in ("delivered", "returned", "cancelled")},
        "orders_with_more_than_one_attempt": sum(1 for v in attempts.values() if v > 1),
        "max_attempts": max(attempts.values()),
        "lines_discount_null": sum(1 for l in lines if l[5] == ""),
        "lines_cancelled": sum(1 for l in lines if l[6] == "cancelled"),
        "customers_without_region": sum(1 for c in t["customers"][1] if c[2] == ""),
        "customers_never_ordered": len(cust_ids - buyers),
        "products_without_category": sum(1 for p in t["products"][1] if p[2] == ""),
        "products_never_sold": sum(1 for p in t["products"][1] if p[0] not in sold),
        "net_revenue_rule": money(net),
        "net_revenue_by_delivery_month": {k: money(v) for k, v in sorted(net_by_month_delivery.items())},
        "sum_qty_times_price_all_lines": money(gross_naive),
        "sum_after_joining_deliveries": money(fanout),
    }


# ---------------------------------------------------------------------------- the mini tables
MINI = {
    "stores": (["store_id", "region", "opened_on", "area_m2"],
               [["S01", "North", "2024-03-01", 820], ["S02", "South", "2023-11-01", 910]]),
    "products": (["product_id", "product_name", "category", "list_price", "is_active"],
                 [["P01", "Fresh milk 1 L", "Dairy", "6.50", "true"], ["P02", "Brown bread loaf", "Bakery", "4.00", "true"],
                  ["P03", "Rice 5 kg", "Pantry", "32.00", "true"], ["P04", "Dish soap 1 L", "", "9.50", "true"],
                  ["P05", "Dates 1 kg", "Pantry", "28.00", "true"]]),
    "customers": (["customer_id", "joined_on", "region", "full_name", "phone", "email", "birth_year", "marketing_opt_in"],
                  [["C001", "2025-02-10", "North", "Synthetic Person 001", "TEL-001-X", "c001@example.invalid", 1988, "true"],
                   ["C002", "2025-05-03", "South", "Synthetic Person 002", "TEL-002-X", "c002@example.invalid", 1995, "false"],
                   ["C003", "2025-07-21", "", "Synthetic Person 003", "TEL-003-X", "c003@example.invalid", 1979, "true"],
                   ["C004", "2025-09-30", "North", "Synthetic Person 004", "TEL-004-X", "c004@example.invalid", 2001, "false"],
                   ["C005", "2026-01-04", "East", "Synthetic Person 005", "TEL-005-X", "c005@example.invalid", 1990, "true"],
                   ["C006", "2026-02-14", "", "Synthetic Person 006", "TEL-006-X", "c006@example.invalid", 1984, "false"]]),
    "orders": (["order_id", "customer_id", "store_id", "ordered_at", "status", "delivery_fee"],
               [["O01", "C001", "S01", "2026-03-01 09:15:00", "delivered", "9.00"],
                ["O02", "C001", "S01", "2026-03-02 18:40:00", "delivered", "0.00"],
                ["O03", "C002", "S02", "2026-03-02 20:05:00", "delivered", "9.00"],
                ["O04", "C002", "S02", "2026-03-03 11:30:00", "cancelled", "9.00"],
                ["O05", "C003", "S02", "2026-03-03 22:50:00", "delivered", "0.00"],
                ["O06", "C004", "S01", "2026-03-04 13:10:00", "returned", "9.00"],
                ["O07", "C005", "S01", "2026-03-04 16:45:00", "delivered", "9.00"],
                ["O08", "C003", "S02", "2026-03-05 10:20:00", "delivered", "9.00"]]),
    "order_lines": (["order_id", "line_no", "product_id", "quantity", "unit_price", "discount", "line_status"],
                    [["O01", 1, "P01", 2, "6.50", "", "ok"], ["O01", 2, "P02", 1, "4.00", "", "ok"],
                     ["O02", 1, "P03", 1, "32.00", "3.20", "ok"], ["O02", 2, "P01", 3, "6.50", "", "ok"],
                     ["O03", 1, "P02", 2, "4.00", "0.00", "ok"], ["O03", 2, "P04", 1, "9.50", "", "cancelled"],
                     ["O04", 1, "P03", 2, "32.00", "", "ok"],
                     ["O05", 1, "P03", 1, "32.00", "", "ok"], ["O05", 2, "P04", 2, "9.50", "1.90", "ok"],
                     ["O06", 1, "P01", 1, "6.50", "", "ok"],
                     ["O07", 1, "P02", 3, "4.00", "", "ok"], ["O07", 2, "P04", 1, "9.50", "", "ok"],
                     ["O08", 1, "P01", 1, "6.50", "", "ok"], ["O08", 2, "P03", 1, "32.00", "", "ok"]]),
    "deliveries": (["delivery_id", "order_id", "attempt_no", "courier_id", "attempted_at", "outcome"],
                   [["D01", "O01", 1, "K01", "2026-03-01 11:00:00", "delivered"],
                    ["D02", "O02", 1, "K01", "2026-03-02 21:30:00", "failed"],
                    ["D03", "O02", 2, "K02", "2026-03-03 12:10:00", "delivered"],
                    ["D04", "O03", 1, "K03", "2026-03-02 22:15:00", "delivered"],
                    ["D05", "O05", 1, "K03", "2026-03-03 23:40:00", "failed"],
                    ["D06", "O05", 2, "K04", "2026-03-04 19:00:00", "failed"],
                    ["D07", "O05", 3, "K03", "2026-03-05 18:30:00", "delivered"],
                    ["D08", "O06", 1, "K02", "2026-03-04 15:00:00", "delivered"],
                    ["D09", "O07", 1, "K01", "2026-03-04 18:20:00", "delivered"],
                    ["D10", "O08", 1, "K04", "2026-03-05 12:00:00", "delivered"]]),
}


# ---------------------------------------------------------------------------- the July extracts
def extracts(rng: Rng):
    """Three raw extracts for July 2026 with seeded defects. Returns rows and the expected log."""
    cust, cust_ok = [], []
    for i in range(1, 301):
        cid = f"C{40000 + i:05d}"
        cust.append([cid, f"2026-07-{1 + (i % 28):02d}", REGIONS[i % 5], f"Synthetic Person {40000 + i:05d}",
                     f"TEL-{40000 + i:05d}-X", f"c{40000 + i:05d}@example.invalid", str(1955 + i % 50),
                     "true" if i % 3 == 0 else "false"])
    # defects: 2 duplicate keys (rows 41 and 42 repeat earlier ids), 3 missing ids, 2 unknown regions, 1 impossible date
    cust.insert(41, list(cust[10]))                                  # exact duplicate of C40011
    dup = list(cust[20]); dup[2] = "East"; cust.insert(120, dup)       # same id C40021, different region
    for pos in (60, 150, 240):
        cust[pos][0] = ""
    bad_region = {cust[75][0]: "Nrth", cust[200][0]: "Wst"}
    cust[75][2], cust[200][2] = "Nrth", "Wst"
    bad_date_id = cust[180][0]
    cust[180][1] = "2026-07-32"
    rejected_customers = set(bad_region) | {bad_date_id}
    valid_customers = {c[0] for c in cust if c[0]} - rejected_customers
    expect_c = {"read": len(cust), "missing key": 3, "duplicate key": 2, "unknown region": 2, "invalid date": 1}

    orders, o_n = [], 0
    cust_ids = [c for c in sorted(valid_customers)]
    for k in range(900):
        o_n += 1
        oid = f"O{300000 + o_n:07d}"
        cid = cust_ids[(k * 7) % len(cust_ids)]
        orders.append([oid, cid, STORES[k % 8][0], f"2026-07-{1 + k % 31:02d} {8 + k % 14:02d}:{(k * 13) % 60:02d}:00",
                       "delivered" if k % 20 else "cancelled", "9.00" if k % 4 else "0.00"])
    # defects
    for pos, cid in zip((30, 130, 230, 330, 430), ("C49901", "C49902", "C49903", "C49904", "C49905")):
        orders[pos][1] = cid                                          # 5 unknown customers
    for pos in (500, 510, 520):
        orders[pos][4] = "deliverd"                                   # 3 invalid statuses
    orders[600][3] = "2026-07-15 25:10:00"; orders[610][3] = "15/07/2026 10:00"   # 2 invalid timestamps
    rc = sorted(rejected_customers)
    for pos, cid in zip((700, 710, 720), rc):
        orders[pos][1] = cid                                          # 3 orders of rejected customers (cascade)
    orders.insert(801, list(orders[800])); orders.insert(851, list(orders[850]))   # 2 duplicate order ids
    rejected_orders = {orders[p][0] for p in (30, 130, 230, 330, 430, 500, 510, 520, 600, 610, 700, 710, 720)}
    expect_o = {"read": len(orders), "duplicate key": 2, "unknown customer": 5 + 3, "invalid status": 3, "invalid timestamp": 2}

    lines = []
    seen = set()
    for o in orders:
        if o[0] in seen:
            continue
        seen.add(o[0])
        n = 1 + (int(o[0][1:]) % 5)
        for ln in range(1, n + 1):
            p = 1 + (int(o[0][1:]) * 31 + ln * 17) % 1160
            lines.append([o[0], str(ln), f"P{p:04d}", str(1 + (ln % 3)), money(300 + (p * 37) % 4000), "" if ln % 4 else "1.00", "ok"])
    # defects
    lines[100][3] = "0"; lines[400][3] = "-1"; lines[700][3] = "0"; lines[1000][3] = "-2"    # 4 non-positive quantities
    lines[1300][4] = "n/a"; lines[1600][4] = "n/a"                                         # 2 unreadable prices
    for pos in (1900, 2100, 2300):
        lines.insert(pos + 1, list(lines[pos]))                                            # 3 duplicate keys
    for pos, oid in zip((150, 450, 750, 1050, 1350, 1650), ("O0399901", "O0399902", "O0399903", "O0399904", "O0399905", "O0399906")):
        lines[pos][0] = oid                                                                # 6 unknown orders
    # the expected log: unknown order includes lines whose order was rejected (cascade)
    known_orders = {o[0] for o in orders} - rejected_orders
    exp = {"read": len(lines), "duplicate key": 0, "unknown order": 0, "invalid quantity": 0, "invalid price": 0}
    keys = set()
    for l in lines:
        k = (l[0], l[1])
        if k in keys:
            exp["duplicate key"] += 1
            continue
        keys.add(k)
        if l[0] not in known_orders:
            exp["unknown order"] += 1
        elif not l[4].replace(".", "", 1).isdigit():
            exp["invalid price"] += 1
        elif int(l[3]) <= 0:
            exp["invalid quantity"] += 1
    return ({"customers_raw": (["customer_id", "joined_on", "region", "full_name", "phone", "email", "birth_year", "marketing_opt_in"], cust),
             "orders_raw": (["order_id", "customer_id", "store_id", "ordered_at", "status", "delivery_fee"], orders),
             "order_lines_raw": (["order_id", "line_no", "product_id", "quantity", "unit_price", "discount", "line_status"], lines)},
            {"customers": expect_c, "orders": expect_o, "order_lines": exp})


def main(argv) -> int:
    small = "--small" in argv
    for name, (h, rows) in MINI.items():
        write_csv(DATA / "mini" / f"{name}.csv", h, rows)
    ex, expect = extracts(Rng(SEED + 1))
    for name, (h, rows) in ex.items():
        write_csv(DATA / "extracts" / f"{name}.csv", h, rows)
    if small:
        print("wrote data/mini and data/extracts")
        return 0
    t = full_tables(Rng(SEED))
    digest = hashlib.sha256()
    for name, (h, rows) in t.items():
        p = DATA / "full" / f"{name}.csv"
        write_csv(p, h, rows)
        digest.update(p.read_bytes())
        print(f"{name:12s} {len(rows):>9,} rows")
    sha = digest.hexdigest()
    (DATA / "full.sha256").write_text(sha + "\n", encoding="utf-8", newline="\n")
    key = key_numbers(t)
    key["load_log_expected"] = expect
    (LABS / "solutions").mkdir(exist_ok=True)
    (LABS / "solutions" / "key_numbers.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("sha256", sha)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
