"""
visualizer.py
Generates 7 professional charts for GitHub proof.
Run: python src/visualizer.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import sys

sys.path.insert(0, "src")
from analyzer import (load_data, category_analysis, monthly_analysis,
                      payment_analysis, top_expenses, overall_summary)

os.makedirs("outputs", exist_ok=True)
plt.style.use("dark_background")

COLORS = {
    "primary":   "#00d4ff",
    "secondary": "#7b2fff",
    "success":   "#00ff88",
    "danger":    "#ff4444",
    "warning":   "#ffcc00",
    "accent":    "#ff6b6b",
}
PALETTE = ["#00d4ff","#7b2fff","#00ff88",
           "#ffcc00","#ff6b6b","#ff9500",
           "#1abc9c","#e74c3c","#9b59b6","#3498db"]

print("Generating charts...")

# ── Load data ─────────────────────────────────────────────────────────────────
expenses, budgets = load_data()
summary   = overall_summary(expenses)
cat       = category_analysis(expenses, budgets)
monthly   = monthly_analysis(expenses)
pay       = payment_analysis(expenses)
top_exp   = top_expenses(expenses, 10)

# ── Chart 1: Category wise spending bar chart ─────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#0a0f1e")
ax.set_facecolor("#0a0f1e")

bars = ax.barh(
    cat["category"], cat["total_spent"],
    color=PALETTE[:len(cat)],
    edgecolor="#020408", linewidth=0.5,
)
for bar, val in zip(bars, cat["total_spent"]):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
            f"₹{val:,.0f}", va="center",
            color="white", fontsize=9)

ax.set_title("💰 Total Spending by Category",
             fontsize=15, fontweight="bold",
             color="white", pad=15)
ax.set_xlabel("Total Amount (₹)", color="#8892b0")
ax.tick_params(colors="white")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#1a2744")
ax.spines["bottom"].set_color("#1a2744")
plt.tight_layout()
plt.savefig("outputs/01_category_spending.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 1 saved")

# ── Chart 2: Monthly spending trend ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor("#0a0f1e")
ax.set_facecolor("#0a0f1e")

ax.plot(monthly["month"], monthly["total_spent"],
        color=COLORS["primary"], linewidth=2.5,
        marker="o", markersize=8,
        markerfacecolor=COLORS["secondary"],
        markeredgecolor=COLORS["primary"],
        markeredgewidth=2)
ax.fill_between(monthly["month"], monthly["total_spent"],
                alpha=0.15, color=COLORS["primary"])

for i, (month, val) in enumerate(zip(
    monthly["month"], monthly["total_spent"]
)):
    ax.annotate(f"₹{val:,.0f}",
                (month, val),
                textcoords="offset points",
                xytext=(0, 12),
                ha="center", fontsize=9,
                color=COLORS["primary"])

ax.set_title("📅 Monthly Spending Trend",
             fontsize=15, fontweight="bold",
             color="white", pad=15)
ax.set_xlabel("Month", color="#8892b0")
ax.set_ylabel("Total Spent (₹)", color="#8892b0")
ax.tick_params(colors="white", axis="x", rotation=20)
ax.tick_params(colors="white", axis="y")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#1a2744")
ax.spines["bottom"].set_color("#1a2744")
ax.grid(True, alpha=0.1, color="#1a2744")
plt.tight_layout()
plt.savefig("outputs/02_monthly_trend.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 2 saved")

# ── Chart 3: Budget vs actual spending ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#0a0f1e")
ax.set_facecolor("#0a0f1e")

months      = expenses["month"].nunique()
budget_total = cat["monthly_budget"] * months
x            = np.arange(len(cat))
width        = 0.35

bars1 = ax.bar(x - width/2, budget_total,
               width, label="Budget",
               color=COLORS["success"],
               alpha=0.7, edgecolor="#020408")
bars2 = ax.bar(x + width/2, cat["total_spent"],
               width, label="Actual Spent",
               color=COLORS["danger"],
               alpha=0.7, edgecolor="#020408")

ax.set_xticks(x)
ax.set_xticklabels(cat["category"],
                   rotation=20, ha="right",
                   color="white", fontsize=9)
ax.set_title("🎯 Budget vs Actual Spending",
             fontsize=15, fontweight="bold",
             color="white", pad=15)
ax.set_ylabel("Amount (₹)", color="#8892b0")
ax.tick_params(colors="white")
ax.legend(facecolor="#0a0f1e",
          labelcolor="white", fontsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#1a2744")
ax.spines["bottom"].set_color("#1a2744")
ax.grid(True, alpha=0.1, axis="y", color="#1a2744")
plt.tight_layout()
plt.savefig("outputs/03_budget_vs_actual.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 3 saved")

# ── Chart 4: Payment method pie chart ────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor("#0a0f1e")

# Pie chart
axes[0].set_facecolor("#0a0f1e")
wedges, texts, autotexts = axes[0].pie(
    pay["total_spent"],
    labels=pay["payment_method"],
    autopct="%1.1f%%",
    colors=PALETTE[:len(pay)],
    startangle=140,
    wedgeprops=dict(edgecolor="#020408", linewidth=2),
)
for text in texts:
    text.set_color("white")
for autotext in autotexts:
    autotext.set_color("#020408")
    autotext.set_fontweight("bold")
axes[0].set_title("💳 Payment Method Distribution",
                  fontsize=13, fontweight="bold",
                  color="white", pad=15)

# Bar chart
axes[1].set_facecolor("#0a0f1e")
axes[1].barh(pay["payment_method"], pay["total_spent"],
             color=PALETTE[:len(pay)],
             edgecolor="#020408")
axes[1].set_title("💳 Spending by Payment Method",
                  fontsize=13, fontweight="bold",
                  color="white", pad=15)
axes[1].set_xlabel("Total Spent (₹)", color="#8892b0")
axes[1].tick_params(colors="white")
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)
axes[1].spines["left"].set_color("#1a2744")
axes[1].spines["bottom"].set_color("#1a2744")

plt.tight_layout()
plt.savefig("outputs/04_payment_methods.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 4 saved")

# ── Chart 5: Essential vs non-essential ──────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor("#0a0f1e")

ess_data = expenses.groupby("is_essential")["amount"].sum()
labels   = ["Non-Essential", "Essential"]
colors   = [COLORS["warning"], COLORS["success"]]

axes[0].set_facecolor("#0a0f1e")
wedges, texts, autotexts = axes[0].pie(
    ess_data.values,
    labels=labels,
    autopct="%1.1f%%",
    colors=colors,
    startangle=90,
    wedgeprops=dict(edgecolor="#020408",
                    linewidth=2),
    explode=(0.05, 0.05),
)
for text in texts:
    text.set_color("white")
    text.set_fontsize(12)
for autotext in autotexts:
    autotext.set_color("#020408")
    autotext.set_fontweight("bold")
axes[0].set_title("🛒 Essential vs Non-Essential",
                  fontsize=13, fontweight="bold",
                  color="white", pad=15)

# Monthly essential breakdown
axes[1].set_facecolor("#0a0f1e")
monthly_ess = expenses.groupby(
    ["month","is_essential"]
)["amount"].sum().unstack(fill_value=0)
monthly_ess.columns = ["Non-Essential","Essential"]
x    = np.arange(len(monthly_ess))
w    = 0.35
axes[1].bar(x - w/2, monthly_ess["Essential"],
            w, label="Essential",
            color=COLORS["success"], alpha=0.8)
axes[1].bar(x + w/2, monthly_ess["Non-Essential"],
            w, label="Non-Essential",
            color=COLORS["warning"], alpha=0.8)
axes[1].set_xticks(x)
axes[1].set_xticklabels(monthly_ess.index,
                         rotation=20, ha="right",
                         color="white", fontsize=9)
axes[1].set_title("📅 Monthly Essential Breakdown",
                  fontsize=13, fontweight="bold",
                  color="white")
axes[1].set_ylabel("Amount (₹)", color="#8892b0")
axes[1].tick_params(colors="white")
axes[1].legend(facecolor="#0a0f1e",
               labelcolor="white")
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)
axes[1].spines["left"].set_color("#1a2744")
axes[1].spines["bottom"].set_color("#1a2744")

plt.tight_layout()
plt.savefig("outputs/05_essential_spending.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 5 saved")

# ── Chart 6: Top 10 biggest expenses ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#0a0f1e")
ax.set_facecolor("#0a0f1e")

colors_top = [PALETTE[i % len(PALETTE)]
              for i in range(len(top_exp))]
bars = ax.barh(
    [f"{r['description'][:25]}\n({r['category']})"
     for _, r in top_exp.iterrows()],
    top_exp["amount"],
    color=colors_top,
    edgecolor="#020408",
)
for bar, val in zip(bars, top_exp["amount"]):
    ax.text(bar.get_width() + 100,
            bar.get_y() + bar.get_height()/2,
            f"₹{val:,.0f}",
            va="center", color="white", fontsize=9)

ax.set_title("💸 Top 10 Biggest Expenses",
             fontsize=15, fontweight="bold",
             color="white", pad=15)
ax.set_xlabel("Amount (₹)", color="#8892b0")
ax.tick_params(colors="white")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#1a2744")
ax.spines["bottom"].set_color("#1a2744")
plt.tight_layout()
plt.savefig("outputs/06_top_expenses.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 6 saved")

# ── Chart 7: Category heatmap by month ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor("#0a0f1e")
ax.set_facecolor("#0a0f1e")

pivot = expenses.pivot_table(
    values="amount",
    index="category",
    columns="month",
    aggfunc="sum",
    fill_value=0
)
sns.heatmap(
    pivot,
    ax=ax,
    cmap="YlOrRd",
    annot=True,
    fmt=".0f",
    linewidths=0.5,
    linecolor="#020408",
    cbar_kws={"label": "Amount (₹)"},
)
ax.set_title("🔥 Category Spending Heatmap by Month",
             fontsize=15, fontweight="bold",
             color="white", pad=15)
ax.set_xlabel("Month", color="#8892b0")
ax.set_ylabel("Category", color="#8892b0")
ax.tick_params(colors="white", axis="x", rotation=20)
ax.tick_params(colors="white", axis="y", rotation=0)
plt.tight_layout()
plt.savefig("outputs/07_category_heatmap.png",
            dpi=150, facecolor="#0a0f1e")
plt.close()
print("✅ Chart 7 saved")

print("\n🎉 All 7 charts saved to outputs/")
print("   Use these as screenshots in your GitHub README!")