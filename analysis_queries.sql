-- ============================================================
-- E-Commerce Sales Analysis — SQL Queries
-- Database: SQLite (table: sales)
-- ============================================================

-- 1. Total revenue, orders, and average order value by month
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_amount), 2) AS total_revenue,
    ROUND(AVG(net_amount), 2) AS avg_order_value
FROM sales
GROUP BY month
ORDER BY month;

-- 2. Revenue and order count by product category
SELECT
    category,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_amount), 2) AS revenue,
    ROUND(SUM(net_amount) * 100.0 / (SELECT SUM(net_amount) FROM sales), 1) AS pct_of_total_revenue
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- 3. Top 10 best-selling products by revenue
SELECT
    product,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(net_amount), 2) AS revenue
FROM sales
GROUP BY product, category
ORDER BY revenue DESC
LIMIT 10;

-- 4. Sales performance by region and channel
SELECT
    region,
    channel,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_amount), 2) AS revenue
FROM sales
GROUP BY region, channel
ORDER BY region, revenue DESC;

-- 5. Customer segmentation: one-time vs. repeat customers
SELECT
    CASE WHEN order_count = 1 THEN 'One-time customer' ELSE 'Repeat customer' END AS customer_type,
    COUNT(*) AS num_customers,
    ROUND(SUM(total_spent), 2) AS total_revenue,
    ROUND(AVG(total_spent), 2) AS avg_spent_per_customer
FROM (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(net_amount) AS total_spent
    FROM sales
    GROUP BY customer_id
) customer_summary
GROUP BY customer_type;

-- 6. Return rate by category (quality/ops signal)
SELECT
    category,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales
GROUP BY category
ORDER BY return_rate_pct DESC;

-- 7. Impact of discounting on order value
SELECT
    CASE
        WHEN discount_pct = 0 THEN 'No discount'
        WHEN discount_pct <= 10 THEN 'Low discount (5-10%)'
        ELSE 'High discount (15-20%)'
    END AS discount_band,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(net_amount), 2) AS avg_order_value
FROM sales
GROUP BY discount_band
ORDER BY avg_order_value DESC;

-- 8. Most preferred payment method by region
SELECT region, payment_method, COUNT(*) AS uses
FROM sales
GROUP BY region, payment_method
ORDER BY region, uses DESC;
