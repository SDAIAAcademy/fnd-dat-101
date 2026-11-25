"""The parallel examples of the slides: the company's returns desk, a department the labs never use.

    uv run python _tools/slide_examples.py      # from labs/: prints every number a slide quotes

The slides teach with these small tables so that no slide gives away a lab answer. Every
number on a slide that comes from them is printed here, under the slide id that shows it.
"""
from __future__ import annotations

import duckdb

SETUP = """
CREATE TABLE reasons (reason_code VARCHAR PRIMARY KEY, label VARCHAR NOT NULL);
INSERT INTO reasons VALUES ('R1','damaged'),('R2','wrong item'),('R3','late'),('R4','expired');
CREATE TABLE returns (
  return_id VARCHAR PRIMARY KEY, order_ref VARCHAR NOT NULL,
  reason_code VARCHAR NOT NULL REFERENCES reasons (reason_code),
  refund DECIMAL(8,2) CHECK (refund >= 0), received_on DATE NOT NULL);
INSERT INTO returns VALUES
 ('T1','O-A11','R1',12.00,'2026-05-02'),('T2','O-A12','R2',30.50,'2026-05-02'),
 ('T3','O-A15','R1',8.25,'2026-05-03'),('T4','O-A15','R3',NULL,'2026-05-04'),
 ('T5','O-A20','R2',19.00,'2026-05-06');
CREATE TABLE return_items (
  return_id VARCHAR NOT NULL REFERENCES returns (return_id), item_no INTEGER NOT NULL,
  product_ref VARCHAR NOT NULL, qty INTEGER NOT NULL CHECK (qty > 0),
  PRIMARY KEY (return_id, item_no));
INSERT INTO return_items VALUES
 ('T1',1,'X-101',2),('T2',1,'X-205',1),('T2',2,'X-118',3),('T3',1,'X-101',1),
 ('T4',1,'X-330',1),('T5',1,'X-205',2),('T5',2,'X-101',1),('T5',3,'X-412',4);
CREATE TABLE inspections (return_id VARCHAR, inspected_on DATE, result VARCHAR);
INSERT INTO inspections VALUES
 ('T2','2026-05-03','pass'),('T2','2026-05-04','fail'),('T5','2026-05-07','pass'),('T1','2026-05-02','pass');
"""

EXAMPLES = {
    # Day 1
    "key-by-counting": "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_ref) AS n_refs FROM returns",
    "key-by-counting-pair": "SELECT COUNT(*) FROM (SELECT DISTINCT return_id, item_no FROM return_items)",
    "measure-cardinality": "SELECT MIN(n), MAX(n) FROM (SELECT return_id, COUNT(*) n FROM return_items GROUP BY return_id)",
    "fewest-is-the-trap": """SELECT r.reason_code, COUNT(t.return_id) AS returns FROM reasons r
                             LEFT JOIN returns t ON t.reason_code = r.reason_code GROUP BY r.reason_code ORDER BY 1""",
    "half-open-dates": "SELECT COUNT(*) FROM returns WHERE received_on >= DATE '2026-05-02' AND received_on < DATE '2026-05-04'",
    "expressions": "SELECT return_id, COALESCE(refund, 0) AS refund_or_zero FROM returns ORDER BY return_id",
    # Day 2
    "case-bands": """SELECT CASE WHEN qty = 1 THEN 'single' WHEN qty <= 3 THEN 'few' ELSE 'many' END AS band,
                     COUNT(*) FROM return_items GROUP BY band ORDER BY band""",
    "set-ops": """SELECT product_ref FROM return_items WHERE return_id IN ('T1','T2')
                  INTERSECT SELECT product_ref FROM return_items WHERE return_id = 'T5'""",
    "null-equals": "SELECT COUNT(*) FROM returns WHERE refund = NULL",
    "null-not-equal": "SELECT COUNT(*) FROM returns WHERE refund <> 12.00",
    "null-is": "SELECT COUNT(*) FROM returns WHERE refund IS NULL",
    "null-aggregates": "SELECT COUNT(*), COUNT(refund), SUM(refund), AVG(refund) FROM returns",
    "group-grain": "SELECT reason_code, COUNT(*) AS returns, SUM(refund) AS refunds FROM returns GROUP BY reason_code ORDER BY 1",
    "having": "SELECT reason_code, COUNT(*) FROM returns GROUP BY reason_code HAVING COUNT(*) >= 2 ORDER BY 1",
    "inner-join": "SELECT COUNT(*) FROM returns t JOIN inspections i ON i.return_id = t.return_id",
    "left-join": "SELECT COUNT(*) FROM returns t LEFT JOIN inspections i ON i.return_id = t.return_id",
    "anti-join": "SELECT t.return_id FROM returns t WHERE NOT EXISTS (SELECT 1 FROM inspections i WHERE i.return_id = t.return_id) ORDER BY 1",
    "semi-join": "SELECT COUNT(*) FROM returns t WHERE EXISTS (SELECT 1 FROM inspections i WHERE i.return_id = t.return_id)",
    # Day 3
    "fan-out-sum": """SELECT SUM(t.refund) FROM returns t JOIN inspections i ON i.return_id = t.return_id""",
    "fan-out-true": """SELECT SUM(refund) FROM returns WHERE return_id IN (SELECT return_id FROM inspections)""",
    "pre-aggregate": """WITH insp AS (SELECT return_id, COUNT(*) AS inspections FROM inspections GROUP BY return_id)
                        SELECT SUM(t.refund), SUM(insp.inspections) FROM returns t JOIN insp ON insp.return_id = t.return_id""",
    "cte-chain": """WITH items AS (SELECT return_id, SUM(qty) AS units FROM return_items GROUP BY return_id)
                    SELECT AVG(units) FROM items""",
    "rank-ties": """SELECT product_ref, SUM(qty) AS units,
                      ROW_NUMBER() OVER (ORDER BY SUM(qty) DESC, product_ref) AS rn,
                      RANK() OVER (ORDER BY SUM(qty) DESC) AS rk,
                      DENSE_RANK() OVER (ORDER BY SUM(qty) DESC) AS drk
                    FROM return_items GROUP BY product_ref ORDER BY units DESC, product_ref""",
    "lag": """SELECT return_id, received_on, received_on - LAG(received_on) OVER (ORDER BY received_on, return_id) AS days_since
              FROM returns ORDER BY received_on, return_id""",
    "running-total": """SELECT return_id, refund, SUM(refund) OVER (ORDER BY return_id) AS running FROM returns ORDER BY return_id""",
    "rows-vs-range": """SELECT received_on, SUM(COALESCE(refund,0)) AS day_refund,
                          AVG(SUM(COALESCE(refund,0))) OVER (ORDER BY received_on ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS avg_rows,
                          AVG(SUM(COALESCE(refund,0))) OVER (ORDER BY received_on RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW) AS avg_range
                        FROM returns GROUP BY received_on ORDER BY received_on""",
}


def main() -> None:
    con = duckdb.connect()
    con.execute(SETUP)
    for slide, sql in EXAMPLES.items():
        cur = con.execute(sql)
        print(f"[{slide}]", [d[0] for d in cur.description])
        for r in cur.fetchall():
            print("   ", r)


if __name__ == "__main__":
    main()
