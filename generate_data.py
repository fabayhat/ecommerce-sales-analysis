"""
Generates a realistic synthetic e-commerce sales dataset for the portfolio project.
No real customer data is used -- everything here is randomly generated.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---- Reference lists ----
categories = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Phone Case", "Laptop Stand", "USB-C Charger", "Smart Watch"],
    "Home & Kitchen": ["Coffee Maker", "Air Fryer", "Blender", "Non-Stick Pan Set", "Storage Containers"],
    "Fashion": ["Running Shoes", "Denim Jacket", "Backpack", "Sunglasses", "Wool Sweater"],
    "Beauty": ["Face Serum", "Shampoo Bar", "Makeup Brush Set", "Body Lotion"],
    "Sports": ["Yoga Mat", "Resistance Bands", "Water Bottle", "Dumbbell Set"],
}

regions = ["North", "South", "East", "West", "Central"]
channels = ["Website", "Mobile App", "Marketplace"]
payment_methods = ["Credit Card", "Debit Card", "Digital Wallet", "Cash on Delivery"]

n_orders = 3000
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
order_id = 100000

for i in range(n_orders):
    order_id += 1
    order_date = start_date + timedelta(days=int(np.random.randint(0, date_range_days)))

    # slight seasonality: more orders in Nov/Dec
    if order_date.month in (11, 12) and np.random.rand() < 0.4:
        order_date = order_date.replace(day=min(order_date.day, 28))

    category = np.random.choice(list(categories.keys()), p=[0.30, 0.22, 0.22, 0.14, 0.12])
    product = np.random.choice(categories[category])

    base_prices = {
        "Electronics": (25, 180), "Home & Kitchen": (20, 150),
        "Fashion": (15, 120), "Beauty": (8, 60), "Sports": (10, 90),
    }
    low, high = base_prices[category]
    unit_price = round(np.random.uniform(low, high), 2)

    quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.15, 0.07, 0.05, 0.03])

    discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20], p=[0.45, 0.1, 0.05, 0.15, 0.13, 0.07, 0.05])
    region = np.random.choice(regions)
    channel = np.random.choice(channels, p=[0.45, 0.4, 0.15])
    payment = np.random.choice(payment_methods, p=[0.4, 0.25, 0.25, 0.1])

    customer_id = np.random.randint(1, 1200)  # repeat customers -> retention analysis
    is_returned = np.random.rand() < 0.04

    gross_amount = round(unit_price * quantity, 2)
    net_amount = round(gross_amount * (1 - discount_pct / 100), 2)

    rows.append([
        order_id, order_date.date().isoformat(), customer_id, category, product,
        quantity, unit_price, discount_pct, gross_amount, net_amount,
        region, channel, payment, is_returned
    ])

df = pd.DataFrame(rows, columns=[
    "order_id", "order_date", "customer_id", "category", "product",
    "quantity", "unit_price", "discount_pct", "gross_amount", "net_amount",
    "region", "channel", "payment_method", "is_returned"
])

df.sort_values("order_date", inplace=True)
df.to_csv("ecommerce_sales.csv", index=False)
print(f"Generated {len(df)} orders -> ecommerce_sales.csv")
print(df.head())
