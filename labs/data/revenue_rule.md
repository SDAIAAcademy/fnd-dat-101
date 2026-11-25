# Net revenue: the finance rule

Kept by the finance controller of the grocery delivery company. This rule is not in the schema:
no column, constraint or view of the database states it. Every report of net revenue follows it.

1. **Orders.** Only orders with status `delivered`. A `returned` order was refunded in full and a
   `cancelled` order was never charged: neither is revenue.
2. **Lines.** Only lines with `line_status` `ok`. A cancelled line was not sent and not charged.
3. **Line revenue.** `quantity * unit_price - discount`. An empty discount (NULL) means no
   discount: count it as 0, never drop the line.
4. **Delivery fees** are reported separately. They are never part of net revenue.
5. **Date.** Revenue is booked on the date of the successful delivery attempt (`deliveries`,
   `outcome = 'delivered'`), not on the date the order was placed. An order placed on the last
   day of a month and delivered the next day belongs to the next month.
6. **Amounts** are in riyals, rounded to two decimals only at the end.
