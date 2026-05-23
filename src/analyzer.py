"""
analyzer.py
Analyzes expense data — category wise,
monthly trends, budget tracking and insights.
Run: python src/analyzer.py
"""

import pandas as pd
import numpy as np
import os

EXPENSES_PATH = "data/expenses.csv"
BUDGETS_PATH  = "data/budgets.csv"

def load_data():
    expenses = pd.read_csv(EXPENSES_PATH, parse_dates=["date"])
    budgets  = pd.read_csv(BUDGETS_PATH)
    return expenses, budgets


def overall_summary(expenses):
    """Calculate overall spending summary."""
    return {
        "total_transactions": len(expenses),
        "total_spent_₹":      round(expenses["amount"].sum(), 2),
        "avg_transaction_₹":  round(expenses["amount"].mean(), 2),
        "max_transaction_₹":  round(expenses["amount"].max(), 2),
        "min_transaction_₹":  round(expenses["amount"].min(), 2),
        "total_months":       expenses["month"].nunique(),
        "avg_monthly_₹":      round(
            expenses["amount"].sum() /
            expenses["month"].nunique(), 2
        ),
        "top_category":       (expenses.groupby("category")["amount"]
                               .sum().idxmax()),
        "top_payment_method": (expenses["payment_method"]
                               .value_counts().idxmax()),
        "essential_spent_₹":  round(
            expenses[expenses["is_essential"] == True]
            ["amount"].sum(), 2
        ),
        "non_essential_₹":    round(
            expenses[expenses["is_essential"] == False]
            ["amount"].sum(), 2
        ),
    }


def category_analysis(expenses, budgets):
    """Analyze spending by category vs budget."""
    cat_spend = (expenses.groupby("category")["amount"]
                 .agg(["sum","mean","count"])
                 .reset_index())
    cat_spend.columns = ["category","total_spent",
                         "avg_spent","transactions"]
    cat_spend["total_spent"] = cat_spend["total_spent"].round(2)
    cat_spend["avg_spent"]   = cat_spend["avg_spent"].round(2)

    # Merge with budgets
    merged = cat_spend.merge(budgets, on="category", how="left")
    merged["budget_used_%"] = (
        merged["total_spent"] /
        (merged["monthly_budget"] * expenses["month"].nunique())
        * 100
    ).round(1)
    merged["status"] = merged["budget_used_%"].apply(
        lambda x: "🔴 Over Budget" if x > 100
        else "🟡 Near Limit" if x > 80
        else "🟢 On Track"
    )
    return merged.sort_values("total_spent", ascending=False)


def monthly_analysis(expenses):
    """Analyze spending month by month."""
    monthly = (expenses.groupby("month")["amount"]
               .agg(["sum","mean","count"])
               .reset_index())
    monthly.columns = ["month","total_spent",
                       "avg_transaction","num_transactions"]
    monthly["total_spent"]     = monthly["total_spent"].round(2)
    monthly["avg_transaction"]  = monthly["avg_transaction"].round(2)
    monthly["mom_change_%"]     = (
        monthly["total_spent"].pct_change() * 100
    ).round(1)
    return monthly


def payment_analysis(expenses):
    """Analyze spending by payment method."""
    pay = (expenses.groupby("payment_method")["amount"]
           .agg(["sum","count"])
           .reset_index())
    pay.columns = ["payment_method","total_spent","transactions"]
    pay["percentage_%"] = (
        pay["total_spent"] / pay["total_spent"].sum() * 100
    ).round(1)
    return pay.sort_values("total_spent", ascending=False)


def top_expenses(expenses, n=10):
    """Get top n biggest expenses."""
    return (expenses.nlargest(n, "amount")
            [["date","category","description",
              "amount","payment_method"]])


def savings_analysis(expenses, budgets):
    """Calculate potential savings per category."""
    cat    = category_analysis(expenses, budgets)
    months = expenses["month"].nunique()
    cat["monthly_budget"]   = cat["monthly_budget"]
    cat["monthly_avg_spend"] = (
        cat["total_spent"] / months
    ).round(2)
    cat["monthly_savings"]  = (
        cat["monthly_budget"] - cat["monthly_avg_spend"]
    ).round(2)
    cat["saving_status"] = cat["monthly_savings"].apply(
        lambda x: "✅ Saving" if x > 0 else "❌ Overspending"
    )
    return cat[["category","monthly_budget",
                "monthly_avg_spend","monthly_savings",
                "saving_status"]]


def get_insights(expenses, budgets):
    """Generate smart spending insights."""
    summary  = overall_summary(expenses)
    cat      = category_analysis(expenses, budgets)
    insights = []

    # Insight 1: Top spending category
    top_cat = cat.iloc[0]
    insights.append(
        f"💸 Your highest spending is on "
        f"'{top_cat['category']}' — "
        f"₹{top_cat['total_spent']:,.0f} total"
    )

    # Insight 2: Over budget categories
    over = cat[cat["budget_used_%"] > 100]
    if not over.empty:
        insights.append(
            f"🔴 {len(over)} categories are over budget: "
            f"{', '.join(over['category'].tolist())}"
        )

    # Insight 3: Essential vs non-essential
    ess_pct = round(
        summary["essential_spent_₹"] /
        summary["total_spent_₹"] * 100, 1
    )
    insights.append(
        f"📊 {ess_pct}% of spending is on essentials, "
        f"{100-ess_pct}% on non-essentials"
    )

    # Insight 4: Top payment method
    insights.append(
        f"💳 Most used payment method: "
        f"{summary['top_payment_method']}"
    )

    # Insight 5: Monthly average
    insights.append(
        f"📅 Average monthly spending: "
        f"₹{summary['avg_monthly_₹']:,.0f}"
    )

    return insights


if __name__ == "__main__":
    print("=" * 55)
    print("  Personal Expense Tracker — Analysis")
    print("=" * 55)

    expenses, budgets = load_data()

    # Overall summary
    summary = overall_summary(expenses)
    print("\n📊 OVERALL SUMMARY:")
    print(f"{'─'*40}")
    for k, v in summary.items():
        print(f"  {k:<25}: {v}")

    # Category analysis
    print("\n📂 CATEGORY ANALYSIS:")
    print(f"{'─'*40}")
    cat = category_analysis(expenses, budgets)
    print(cat[["category","total_spent",
               "budget_used_%","status"]]
          .to_string(index=False))

    # Monthly analysis
    print("\n📅 MONTHLY ANALYSIS:")
    print(f"{'─'*40}")
    monthly = monthly_analysis(expenses)
    print(monthly.to_string(index=False))

    # Payment analysis
    print("\n💳 PAYMENT METHOD ANALYSIS:")
    print(f"{'─'*40}")
    pay = payment_analysis(expenses)
    print(pay.to_string(index=False))

    # Top expenses
    print("\n💰 TOP 5 BIGGEST EXPENSES:")
    print(f"{'─'*40}")
    print(top_expenses(expenses, 5).to_string(index=False))

    # Insights
    print("\n💡 SMART INSIGHTS:")
    print(f"{'─'*40}")
    for insight in get_insights(expenses, budgets):
        print(f"  {insight}")

    print("\n✅ Analysis complete!")