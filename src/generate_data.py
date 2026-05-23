"""
generate_data.py
Generates synthetic personal expense data.
Run: python src/generate_data.py
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

fake = Faker()
SEED = 42
random.seed(SEED)
Faker.seed(SEED)
np.random.seed(SEED)

# ── Categories & budgets ──────────────────────────────────────────────────────
CATEGORIES = {
    "Food & Dining":     {"budget": 5000,  "min": 50,   "max": 800},
    "Transportation":    {"budget": 3000,  "min": 20,   "max": 500},
    "Shopping":          {"budget": 4000,  "min": 100,  "max": 3000},
    "Entertainment":     {"budget": 2000,  "min": 100,  "max": 1500},
    "Bills & Utilities": {"budget": 3000,  "min": 200,  "max": 2500},
    "Health & Fitness":  {"budget": 2000,  "min": 100,  "max": 1500},
    "Education":         {"budget": 3000,  "min": 500,  "max": 5000},
    "Travel":            {"budget": 5000,  "min": 500,  "max": 10000},
    "Groceries":         {"budget": 4000,  "min": 100,  "max": 2000},
    "Personal Care":     {"budget": 1500,  "min": 50,   "max": 1000},
}

PAYMENT_METHODS = [
    "UPI", "Credit Card", "Debit Card",
    "Cash", "Net Banking", "Wallet"
]

DESCRIPTIONS = {
    "Food & Dining":     ["Zomato order", "Swiggy order",
                          "Restaurant dinner", "Cafe coffee",
                          "Street food", "McDonalds"],
    "Transportation":    ["Uber ride", "Ola cab", "Auto rickshaw",
                          "Metro card recharge", "Petrol", "Bus pass"],
    "Shopping":          ["Amazon order", "Flipkart order",
                          "Myntra clothes", "Electronics",
                          "Home decor", "Gift purchase"],
    "Entertainment":     ["Netflix subscription", "Movie tickets",
                          "Spotify premium", "Gaming",
                          "Concert tickets", "OTT subscription"],
    "Bills & Utilities": ["Electricity bill", "Water bill",
                          "Internet bill", "Mobile recharge",
                          "Gas cylinder", "DTH recharge"],
    "Health & Fitness":  ["Gym membership", "Medicine",
                          "Doctor consultation", "Health checkup",
                          "Yoga class", "Protein supplement"],
    "Education":         ["Online course", "Books",
                          "Coaching fees", "Exam fees",
                          "Stationery", "Udemy course"],
    "Travel":            ["Flight ticket", "Hotel booking",
                          "Train ticket", "Bus booking",
                          "Holiday package", "Visa fees"],
    "Groceries":         ["BigBasket order", "Blinkit order",
                          "Supermarket shopping", "Vegetables",
                          "Dairy products", "Weekly groceries"],
    "Personal Care":     ["Salon visit", "Skincare products",
                          "Haircut", "Spa treatment",
                          "Cosmetics", "Grooming kit"],
}


def generate_expenses(months=6, expenses_per_month=40):
    """Generate realistic monthly expense data."""
    expenses = []
    start_date = datetime.now() - timedelta(days=months * 30)

    for month_offset in range(months):
        month_start = start_date + timedelta(days=month_offset * 30)

        for _ in range(expenses_per_month):
            category = random.choice(list(CATEGORIES.keys()))
            cat_info  = CATEGORIES[category]
            amount    = round(random.uniform(
                cat_info["min"], cat_info["max"]
            ), 2)
            date = month_start + timedelta(
                days=random.randint(0, 29)
            )
            expenses.append({
                "date":           date.strftime("%Y-%m-%d"),
                "month":          date.strftime("%B %Y"),
                "category":       category,
                "description":    random.choice(
                    DESCRIPTIONS[category]
                ),
                "amount":         amount,
                "payment_method": random.choice(PAYMENT_METHODS),
                "is_essential":   category in [
                    "Food & Dining", "Bills & Utilities",
                    "Groceries", "Health & Fitness",
                    "Transportation"
                ],
            })

    df = pd.DataFrame(expenses)
    df = df.sort_values("date").reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    return df


def generate_budgets():
    """Generate monthly budget for each category."""
    budgets = []
    for category, info in CATEGORIES.items():
        budgets.append({
            "category": category,
            "monthly_budget": info["budget"],
        })
    return pd.DataFrame(budgets)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("💰 Generating Personal Expense Data...")

    expenses = generate_expenses(months=6, expenses_per_month=40)
    budgets  = generate_budgets()

    expenses.to_csv("data/expenses.csv",  index=False)
    budgets.to_csv("data/budgets.csv",    index=False)

    print(f"✅ expenses.csv → {len(expenses)} transactions")
    print(f"✅ budgets.csv  → {len(budgets)} categories")
    print(f"\n📊 Summary:")
    print(f"   Total Spent  : ₹{expenses['amount'].sum():,.2f}")
    print(f"   Avg/Month    : ₹{expenses['amount'].sum()/6:,.2f}")
    print(f"   Top Category : {expenses.groupby('category')['amount'].sum().idxmax()}")
    print(f"\n📋 Sample Data:")
    print(expenses.head())