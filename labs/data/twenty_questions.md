# The twenty questions

From the head of commercial reporting of the grocery delivery company, to the analyst.
All data covers orders placed from 1 January to 30 June 2026. Amounts are in riyals.

Write a prediction before each query: the number of rows, or a rough value, or the first row.
The automatic checker compares your result with the reference: same columns in the stated
order, same rows. Where an order is stated, the rows must come in that order.

| # | Lab | Question | Columns, and order of rows |
|---|---|---|---|
| 1 | 1.4 | Which Dairy products have "cheese" in their name, in any letter case? | `product_id, product_name`, by `product_id` |
| 2 | 1.4 | How many orders, of any status, were placed in March 2026? | `orders` |
| 3 | 1.4 | Which are the ten most expensive active products by list price? Break ties by product id. | `product_id, product_name, list_price`, by price from the highest, then `product_id` |
| 4 | 1.4 | What is the value of each line of order O0000018: quantity times unit price, minus the discount (an empty discount means none)? | `line_no, line_value`, by `line_no` |
| 5 | 2.1 | How many order lines fall in each quantity band: `single` (1), `few` (2 or 3), `many` (4 or more)? | `band, lines` |
| 6 | 2.1 | For each order status, how many orders paid a delivery fee and how many did not? | `status, paid, free` |
| 7 | 2.1 | How many customers placed an order in January 2026 but none in June 2026? | `customers` |
| 8 | 2.3 | How many delivered orders did each store dispatch? | `store_id, orders`, by `store_id` |
| 9 | 2.3 | Which customers placed at least 48 orders of any status? | `customer_id, orders`, by orders from the most, then `customer_id` |
| 10 | 2.3 | For each month, by the date the order was placed: how many orders, and how many different customers? | `month, orders, customers` (month as its first day), by `month` |
| 11 | 2.3 | Which products appear on at least 4,000 order lines? | `product_id, lines`, by lines from the most, then `product_id` |
| 12 | 2.4 | How many delivered orders came from the stores of each region? | `region, orders`, by `region` |
| 13 | 2.4 | For each customer region, with `none` where the region is missing: how many customers, and how many of them never ordered? | `region, customers, never_ordered`, by `region` |
| 14 | 2.4 | Which products are listed as active but were never sold? | `product_id, product_name`, by `product_id` |
| 15 | 2.4 | How many customers had at least one order with a failed delivery attempt? | `customers` |
| 16 | 3.1 | What is the total line value (quantity times unit price, lines with status ok) of the orders that needed more than one delivery attempt? Count each line once. | `line_value` |
| 17 | 3.1 | For each store: how many orders had at least one delivery attempt, and how many attempts were made? | `store_id, orders, attempts`, by `store_id` |
| 18 | 3.2 | In each category, how many products have a list price above the average list price of their own category? Leave out products without a category. | `category, products`, by `category` |
| 19 | 3.2 | What was the net revenue in each month, by the finance rule (`revenue_rule.md`)? | `month, net_revenue` (month as its first day), by `month` |
| 20 | 3.2 | Which five customers brought the most net revenue by the finance rule, and how many delivered orders did each have? | `customer_id, net_revenue, delivered_orders`, by net revenue from the highest |
