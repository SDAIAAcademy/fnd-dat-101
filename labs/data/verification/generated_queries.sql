-- Ten generated queries for lab 4.4
--
-- Where they come from: these ten queries were written for this course to reproduce mistakes
-- that SQL generated from a question often contains. No model produced them, and no model output
-- is quoted here. Each was written from the question alone and the schema, the way an assistant
-- that has not read data/revenue_rule.md would write it. Some are right. Your tests decide which.

-- name: v01
-- question: What is the total net revenue?
SELECT SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
JOIN deliveries d ON d.order_id = o.order_id
WHERE o.status = 'delivered' AND l.line_status = 'ok'
;

-- name: v02
-- question: What was the net revenue booked on 3 March 2026?
SELECT SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status = 'delivered' AND l.line_status = 'ok'
  AND CAST(o.ordered_at AS DATE) = DATE '2026-03-03'
;

-- name: v03
-- question: How many orders were delivered?
SELECT COUNT(*) AS delivered_orders
FROM orders
WHERE status = 'delivered'
;

-- name: v04
-- question: What is the average net revenue per delivered order?
SELECT ROUND(AVG(l.quantity * l.unit_price - COALESCE(l.discount, 0)), 2) AS avg_per_order
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status = 'delivered' AND l.line_status = 'ok'
;

-- name: v05
-- question: What is the net revenue of store S02?
SELECT SUM(l.quantity * l.unit_price) AS net_revenue
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.store_id = 'S02' AND o.status = 'delivered' AND l.line_status = 'ok'
;

-- name: v06
-- question: How many customers had at least one delivered order?
SELECT COUNT(DISTINCT customer_id) AS customers
FROM orders
WHERE status = 'delivered'
;

-- name: v07
-- question: What is the net revenue of store S01?
SELECT SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.store_id = 'S01' AND o.status <> 'cancelled' AND l.line_status = 'ok'
;

-- name: v08
-- question: How many order lines were cancelled?
SELECT COUNT(*) AS cancelled_lines
FROM order_lines
WHERE line_status = 'cancelled'
;

-- name: v09
-- question: What was the net revenue of March 2026, by month of delivery?
WITH delivered AS (
  SELECT d.order_id, CAST(d.attempted_at AS DATE) AS delivered_on
  FROM deliveries d
  JOIN orders o ON o.order_id = d.order_id
  WHERE d.outcome = 'delivered' AND o.status = 'delivered'
)
SELECT SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM order_lines l
JOIN delivered dv ON dv.order_id = l.order_id
WHERE l.line_status = 'ok'
  AND dv.delivered_on >= DATE '2026-03-01' AND dv.delivered_on < DATE '2026-04-01'
;

-- name: v10
-- question: Which customer brought the most net revenue, and how much?
SELECT o.customer_id, SUM(l.quantity * l.unit_price - COALESCE(l.discount, 0)) AS net_revenue
FROM orders o
JOIN order_lines l ON l.order_id = o.order_id
JOIN deliveries d ON d.order_id = o.order_id
WHERE o.status = 'delivered' AND l.line_status = 'ok'
GROUP BY o.customer_id
ORDER BY net_revenue DESC
LIMIT 1
;
