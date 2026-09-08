"""
Loads ecommerce_sales.csv into a SQLite database, runs the business
analysis queries from analysis_queries.sql, and generates charts.
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ---- Load data into SQLite ----
conn = sqlite3.connect("sales.db")
df = pd.read_csv("ecommerce_sales.csv")
df.to_sql("sales", conn, if_exists="replace", index=False)
print(f"Loaded {len(df)} rows into sales.db\n")

def run_query(sql, title):
    result = pd.read_sql_query(sql, conn)
    print(f"--- {title} ---")
    print(result.to_string(index=False))
    print()
    return result

# 1. Monthly revenue trend
monthly = run_query("""
    SELECT strftime('%Y-%m', order_date) AS month,
           COUNT(DISTINCT order_id) AS total_orders,
           ROUND(SUM(net_amount), 2) AS total_revenue,
           ROUND(AVG(net_amount), 2) AS avg_order_value
    FROM sales GROUP BY month ORDER BY month;
""", "Monthly Revenue Trend")

# 2. Revenue by category
category_rev = run_query("""
    SELECT category, COUNT(DISTINCT order_id) AS orders,
           ROUND(SUM(net_amount), 2) AS revenue
    FROM sales GROUP BY category ORDER BY revenue DESC;
""", "Revenue by Category")

# 3. Top products
top_products = run_query("""
    SELECT product, category, SUM(quantity) AS units_sold,
           ROUND(SUM(net_amount), 2) AS revenue
    FROM sales GROUP BY product, category ORDER BY revenue DESC LIMIT 10;
""", "Top 10 Products by Revenue")

# 4. Region x Channel
region_channel = run_query("""
    SELECT region, channel, COUNT(DISTINCT order_id) AS orders,
           ROUND(SUM(net_amount), 2) AS revenue
    FROM sales GROUP BY region, channel ORDER BY region, revenue DESC;
""", "Region x Channel Performance")

# 5. Customer segmentation
customer_seg = run_query("""
    SELECT CASE WHEN order_count = 1 THEN 'One-time customer' ELSE 'Repeat customer' END AS customer_type,
           COUNT(*) AS num_customers,
           ROUND(SUM(total_spent), 2) AS total_revenue,
           ROUND(AVG(total_spent), 2) AS avg_spent_per_customer
    FROM (SELECT customer_id, COUNT(DISTINCT order_id) AS order_count, SUM(net_amount) AS total_spent
          FROM sales GROUP BY customer_id) t
    GROUP BY customer_type;
""", "Customer Segmentation")

# 6. Return rate by category
returns = run_query("""
    SELECT category, COUNT(*) AS total_orders,
           SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) AS returned_orders,
           ROUND(SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
    FROM sales GROUP BY category ORDER BY return_rate_pct DESC;
""", "Return Rate by Category")

# 7. Discount impact
discount_impact = run_query("""
    SELECT CASE WHEN discount_pct = 0 THEN 'No discount'
                WHEN discount_pct <= 10 THEN 'Low discount (5-10%)'
                ELSE 'High discount (15-20%)' END AS discount_band,
           COUNT(DISTINCT order_id) AS orders,
           ROUND(AVG(net_amount), 2) AS avg_order_value
    FROM sales GROUP BY discount_band ORDER BY avg_order_value DESC;
""", "Discount Impact on Order Value")

conn.close()

# ============================================================
# CHARTS
# ============================================================
plt.style.use("seaborn-v0_8-whitegrid")

# Chart 1: Monthly revenue trend
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["month"], monthly["total_revenue"], marker="o", color="#2E5EAA", linewidth=2)
ax.set_title("Monthly Revenue Trend (2024–2025)", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("chart_monthly_revenue.png", dpi=150)
plt.close()

# Chart 2: Revenue by category
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(category_rev["category"], category_rev["revenue"], color="#3D8B7D")
ax.set_title("Revenue by Product Category", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue ($)")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("chart_category_revenue.png", dpi=150)
plt.close()

# Chart 3: Top 10 products
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(top_products["product"][::-1], top_products["revenue"][::-1], color="#C1666B")
ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold")
ax.set_xlabel("Revenue ($)")
plt.tight_layout()
plt.savefig("chart_top_products.png", dpi=150)
plt.close()

# Chart 4: Return rate by category
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(returns["category"], returns["return_rate_pct"], color="#D9A441")
ax.set_title("Return Rate by Category (%)", fontsize=14, fontweight="bold")
ax.set_ylabel("Return Rate (%)")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("chart_return_rate.png", dpi=150)
plt.close()

print("Charts saved: chart_monthly_revenue.png, chart_category_revenue.png, "
      "chart_top_products.png, chart_return_rate.png")

# Save summary tables for the README
category_rev.to_csv("summary_category_revenue.csv", index=False)
top_products.to_csv("summary_top_products.csv", index=False)
customer_seg.to_csv("summary_customer_segmentation.csv", index=False)
returns.to_csv("summary_return_rate.csv", index=False)
discount_impact.to_csv("summary_discount_impact.csv", index=False)
