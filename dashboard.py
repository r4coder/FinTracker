"""
dashboard.py — Elite Personal Expense Tracker Dashboard
Run: python -m streamlit run dashboard.py
Opens: http://localhost:8501
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, "src")
from analyzer import (load_data, overall_summary, category_analysis,
                      monthly_analysis, payment_analysis,
                      top_expenses, savings_analysis, get_insights)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Elite CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
  * { font-family: 'Inter', sans-serif !important; }
  .stApp { background: #020408; }

  section[data-testid="stSidebar"] {
      background: linear-gradient(180deg,#0a0f1e,#050810) !important;
      border-right: 1px solid #1a2744;
  }
  [data-testid="stMetric"] {
      background: linear-gradient(135deg,#0a0f1e,#0d1526);
      border: 1px solid #1a2744;
      border-radius: 16px;
      padding: 20px !important;
      position: relative; overflow: hidden;
  }
  [data-testid="stMetric"]::before {
      content:''; position:absolute;
      top:0; left:0; right:0; height:2px;
      background: linear-gradient(90deg,#00d4ff,#7b2fff,#00ff88);
  }
  [data-testid="stMetricValue"] {
      font-size:2rem !important; font-weight:900 !important;
      background: linear-gradient(135deg,#00d4ff,#7b2fff);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
  }
  [data-testid="stMetricLabel"] {
      color:#8892b0 !important; font-size:0.75rem !important;
      text-transform:uppercase; letter-spacing:1px;
  }
  .hero-card {
      background: linear-gradient(135deg,#0a0f1e,#0d1526,#0a0f1e);
      border: 1px solid #1a2744; border-radius:20px;
      padding:30px; margin:10px 0;
      position:relative; overflow:hidden;
  }
  .hero-card::before {
      content:''; position:absolute;
      top:0; left:0; right:0; height:3px;
      background: linear-gradient(90deg,#00d4ff,#7b2fff,#00ff88,#00d4ff);
      background-size:200% 100%;
      animation: move 3s linear infinite;
  }
  @keyframes move {
      0%{background-position:0%} 100%{background-position:200%}
  }
  .insight-card {
      background:#0a0f1e; border:1px solid #1a2744;
      border-radius:12px; padding:14px 18px;
      margin:8px 0; color:#ccd6f6; font-size:0.95rem;
      border-left:4px solid #00d4ff;
  }
  .over-budget  { border-left:4px solid #ff4444 !important; }
  .near-limit   { border-left:4px solid #ffcc00 !important; }
  .on-track     { border-left:4px solid #00ff88 !important; }
  .stButton>button {
      background:linear-gradient(135deg,#00d4ff,#7b2fff) !important;
      color:white !important; border:none !important;
      border-radius:10px !important; font-weight:700 !important;
      padding:10px 24px !important;
  }
  .section-header {
      font-size:1.2rem; font-weight:700; color:#ccd6f6;
      margin:20px 0 10px; padding-left:12px;
      border-left:3px solid #00d4ff;
  }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,15,30,0.8)",
    font=dict(family="Inter", color="#8892b0"),
)
GRAD = ["#00d4ff","#7b2fff","#00ff88","#ffcc00",
        "#ff6b6b","#ff9500","#1abc9c","#e74c3c",
        "#9b59b6","#3498db"]

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    expenses, budgets = load_data()
    return expenses, budgets

expenses, budgets = load_all()
summary  = overall_summary(expenses)
cat      = category_analysis(expenses, budgets)
monthly  = monthly_analysis(expenses)
pay      = payment_analysis(expenses)
insights = get_insights(expenses, budgets)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:20px 0'>
  <div style='font-size:3rem'>💰</div>
  <div style='font-size:1.3rem;font-weight:900;
    background:linear-gradient(135deg,#00d4ff,#7b2fff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent'>
    Expense Tracker
  </div>
  <div style='color:#8892b0;font-size:0.8rem'>
    Personal Finance Dashboard
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio("", [
    "🏠 Overview",
    "📂 Category Analysis",
    "📅 Monthly Trends",
    "💳 Payment Methods",
    "🎯 Budget Tracker",
    "💡 Smart Insights",
    "➕ Add Expense",
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
c1, c2 = st.sidebar.columns(2)
c1.metric("Total",   f"₹{summary['total_spent_₹']:,.0f}")
c2.metric("Avg/Mo",  f"₹{summary['avg_monthly_₹']:,.0f}")
c1.metric("Months",  summary["total_months"])
c2.metric("Txns",    summary["total_transactions"])

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown("""
    <div class='hero-card'>
      <h1 style='margin:0;font-size:2.2rem;font-weight:900;
        background:linear-gradient(135deg,#00d4ff,#7b2fff,#00ff88);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent'>
        💰 Personal Expense Tracker
      </h1>
      <p style='color:#8892b0;margin:8px 0 0;font-size:1rem'>
        Track • Analyze • Save — Your complete financial dashboard
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("💸 Total Spent",   f"₹{summary['total_spent_₹']:,.0f}")
    c2.metric("📅 Monthly Avg",   f"₹{summary['avg_monthly_₹']:,.0f}")
    c3.metric("🧾 Transactions",   summary["total_transactions"])
    c4.metric("📊 Avg Txn",       f"₹{summary['avg_transaction_₹']:,.0f}")
    c5.metric("✅ Essential",      f"₹{summary['essential_spent_₹']:,.0f}")
    c6.metric("🎮 Non-Essential",  f"₹{summary['non_essential_₹']:,.0f}")

    st.markdown("---")

    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.markdown('<div class="section-header">📈 Monthly Spending Trend</div>',
                    unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["total_spent"],
            mode="lines+markers",
            line=dict(color="#00d4ff", width=3),
            marker=dict(size=10, color="#7b2fff",
                        line=dict(color="#00d4ff", width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.1)",
            name="Monthly Spend",
        ))
        for i, row in monthly.iterrows():
            fig.add_annotation(
                x=row["month"], y=row["total_spent"],
                text=f"₹{row['total_spent']:,.0f}",
                showarrow=False, yshift=18,
                font=dict(color="#00d4ff", size=11)
            )
        fig.update_layout(**PT, height=320,
                          xaxis_tickangle=-20,
                          margin=dict(t=20,b=60,l=20,r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">🥧 Category Split</div>',
                    unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=cat["category"],
            values=cat["total_spent"],
            hole=0.6,
            marker=dict(colors=GRAD,
                        line=dict(color="#020408", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, color="white"),
        ))
        fig_pie.add_annotation(
            text=f"<b>₹{summary['total_spent_₹']:,.0f}</b><br>Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#00d4ff")
        )
        fig_pie.update_layout(**PT, height=320,
                              showlegend=False,
                              margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="section-header">🔥 Spending Heatmap</div>',
                unsafe_allow_html=True)
    pivot = expenses.pivot_table(
        values="amount", index="category",
        columns="month", aggfunc="sum", fill_value=0
    )
    fig_heat = px.imshow(
        pivot, text_auto=".0f",
        color_continuous_scale=[
            [0,"#0a0f1e"],[0.5,"#7b2fff"],[1,"#00d4ff"]
        ],
        aspect="auto",
    )
    fig_heat.update_traces(textfont=dict(color="white", size=12))
    fig_heat.update_layout(**PT, height=350,
                           margin=dict(t=20,b=20,l=20,r=20),
                           coloraxis_showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CATEGORY ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📂 Category Analysis":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>📂 Category Analysis</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        Deep dive into spending by category
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">💰 Spending by Category</div>',
                    unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=cat["total_spent"],
            y=cat["category"],
            orientation="h",
            marker=dict(
                color=cat["total_spent"],
                colorscale=[[0,"#7b2fff"],[1,"#00d4ff"]],
                showscale=False,
            ),
            text=[f"₹{v:,.0f}" for v in cat["total_spent"]],
            textposition="outside",
            textfont=dict(color="white", size=11),
            cliponaxis=False,
        ))
        fig_bar.update_layout(**PT, height=420,
                              xaxis_title="Total Spent (₹)",
                              margin=dict(t=20,b=20,l=20,r=120))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">📊 Budget Used %</div>',
                    unsafe_allow_html=True)
        colors_budget = [
            "#ff4444" if x > 100
            else "#ffcc00" if x > 80
            else "#00ff88"
            for x in cat["budget_used_%"]
        ]
        fig_budget = go.Figure(go.Bar(
            x=cat["budget_used_%"],
            y=cat["category"],
            orientation="h",
            marker_color=colors_budget,
            text=[f"{v}%" for v in cat["budget_used_%"]],
            textposition="outside",
            textfont=dict(color="white", size=11),
            cliponaxis=False,
        ))
        fig_budget.add_vline(x=100, line_dash="dash",
                             line_color="white",
                             annotation_text="Budget Limit")
        fig_budget.update_layout(**PT, height=420,
                                 xaxis_title="Budget Used (%)",
                                 margin=dict(t=20,b=20,l=20,r=80))
        st.plotly_chart(fig_budget, use_container_width=True)

    st.markdown('<div class="section-header">📋 Category Details</div>',
                unsafe_allow_html=True)
    st.dataframe(
        cat[["category","total_spent","avg_spent",
             "transactions","budget_used_%","status"]],
        use_container_width=True,
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MONTHLY TRENDS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📅 Monthly Trends":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>📅 Monthly Trends</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        Track how your spending changes month over month
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=["Total Monthly Spending",
                                        "Number of Transactions"],
                        vertical_spacing=0.18)
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["total_spent"],
        marker=dict(
            color=monthly["total_spent"],
            colorscale=[[0,"#7b2fff"],[1,"#00d4ff"]],
        ),
        text=[f"₹{v:,.0f}" for v in monthly["total_spent"]],
        textposition="outside",
        textfont=dict(color="white", size=11),
        cliponaxis=False,
        name="Total Spent",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["num_transactions"],
        marker_color="#00ff88",
        text=monthly["num_transactions"],
        textposition="outside",
        textfont=dict(color="white", size=11),
        cliponaxis=False,
        name="Transactions",
    ), row=2, col=1)
    fig.update_yaxes(range=[0, monthly["total_spent"].max() * 1.18], row=1, col=1)
    fig.update_yaxes(range=[0, monthly["num_transactions"].max() * 1.18], row=2, col=1)
    fig.update_layout(**PT, height=580,
                      showlegend=False,
                      margin=dict(t=50,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">📈 Category Trends Over Months</div>',
                unsafe_allow_html=True)
    cat_monthly = expenses.groupby(
        ["month","category"]
    )["amount"].sum().reset_index()

    selected_cats = st.multiselect(
        "Select categories",
        expenses["category"].unique().tolist(),
        default=expenses["category"].unique().tolist()[:4]
    )
    fig_line = go.Figure()
    for i, category in enumerate(selected_cats):
        data = cat_monthly[cat_monthly["category"]==category]
        fig_line.add_trace(go.Scatter(
            x=data["month"], y=data["amount"],
            mode="lines+markers", name=category,
            line=dict(color=GRAD[i % len(GRAD)], width=2),
            marker=dict(size=8),
        ))
    fig_line.update_layout(**PT, height=380,
                           xaxis_tickangle=-20,
                           yaxis_title="Amount (₹)",
                           margin=dict(t=20,b=60,l=20,r=20))
    st.plotly_chart(fig_line, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PAYMENT METHODS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💳 Payment Methods":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>💳 Payment Methods</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        Analyze how you pay for your expenses
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🥧 Payment Split</div>',
                    unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=pay["payment_method"],
            values=pay["total_spent"],
            hole=0.55,
            marker=dict(colors=GRAD[:len(pay)],
                        line=dict(color="#020408", width=2)),
            textinfo="label+percent",
            textfont=dict(color="white", size=12),
        ))
        fig_pie.update_layout(**PT, height=380,
                              showlegend=False,
                              margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">📊 Amount by Method</div>',
                    unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=pay["payment_method"],
            y=pay["total_spent"],
            marker=dict(color=GRAD[:len(pay)],
                        line=dict(color="#020408", width=1)),
            text=[f"₹{v:,.0f}" for v in pay["total_spent"]],
            textposition="outside",
            textfont=dict(color="white", size=11),
            cliponaxis=False,
        ))
        fig_bar.update_yaxes(range=[0, pay["total_spent"].max() * 1.18])
        fig_bar.update_layout(**PT, height=380,
                              yaxis_title="Total Spent (₹)",
                              margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="section-header">📋 Payment Details</div>',
                unsafe_allow_html=True)
    st.dataframe(pay, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — BUDGET TRACKER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Budget Tracker":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>🎯 Budget Tracker</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        Track your spending against monthly budgets
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    months   = expenses["month"].nunique()
    over     = cat[cat["budget_used_%"] > 100]
    near     = cat[(cat["budget_used_%"] > 80) & (cat["budget_used_%"] <= 100)]
    on_track = cat[cat["budget_used_%"] <= 80]

    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Over Budget", len(over))
    c2.metric("🟡 Near Limit",  len(near))
    c3.metric("🟢 On Track",    len(on_track))

    st.markdown("---")

    st.markdown('<div class="section-header">📊 Budget Usage per Category</div>',
                unsafe_allow_html=True)

    for _, row in cat.iterrows():
        raw_pct = row["budget_used_%"]
        # FIX: safely handle NaN before passing to progress()
        pct = 0 if pd.isna(raw_pct) else max(0, min(100, int(raw_pct)))
        color = ("#ff4444" if raw_pct > 100
                 else "#ffcc00" if raw_pct > 80
                 else "#00ff88")
        col_a, col_b, col_c = st.columns([2, 3, 1])
        col_a.markdown(
            f"<span style='color:white'>{row['category']}</span>",
            unsafe_allow_html=True)
        col_b.progress(pct)
        col_c.markdown(
            f"<span style='color:{color};font-weight:700'>"
            f"{raw_pct}%</span>",
            unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="section-header">💰 Savings Analysis</div>',
                unsafe_allow_html=True)
    savings = savings_analysis(expenses, budgets)
    fig_sav = go.Figure(go.Bar(
        x=savings["monthly_savings"],
        y=savings["category"],
        orientation="h",
        marker_color=[
            "#00ff88" if v > 0 else "#ff4444"
            for v in savings["monthly_savings"]
        ],
        text=[f"₹{v:,.0f}" for v in savings["monthly_savings"]],
        textposition="outside",
        textfont=dict(color="white", size=11),
        cliponaxis=False,
    ))
    fig_sav.add_vline(x=0, line_color="white", line_dash="dash")
    fig_sav.update_layout(**PT, height=400,
                          xaxis_title="Monthly Savings (₹)",
                          margin=dict(t=20,b=20,l=20,r=100))
    st.plotly_chart(fig_sav, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 6 — SMART INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💡 Smart Insights":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>💡 Smart Insights</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        AI-powered insights about your spending habits
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="section-header">🔍 Spending Insights</div>',
                unsafe_allow_html=True)
    for insight in insights:
        st.markdown(
            f'<div class="insight-card">{insight}</div>',
            unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🛒 Essential vs Non-Essential</div>',
                    unsafe_allow_html=True)
        ess_data = expenses.groupby("is_essential")["amount"].sum()
        fig_ess = go.Figure(go.Pie(
            labels=["Non-Essential","Essential"],
            values=ess_data.values,
            hole=0.6,
            marker=dict(
                colors=["#ffcc00","#00ff88"],
                line=dict(color="#020408", width=2)
            ),
            textinfo="label+percent",
            textfont=dict(color="white", size=12),
        ))
        fig_ess.update_layout(**PT, height=320,
                              showlegend=False,
                              margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_ess, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">💸 Top 5 Biggest Expenses</div>',
                    unsafe_allow_html=True)
        top5 = top_expenses(expenses, 5)
        fig_top = go.Figure(go.Bar(
            x=top5["amount"],
            y=[d[:20] for d in top5["description"]],
            orientation="h",
            marker=dict(
                color=top5["amount"],
                colorscale=[[0,"#7b2fff"],[1,"#ff4444"]],
                showscale=False,
            ),
            text=[f"₹{v:,.0f}" for v in top5["amount"]],
            textposition="outside",
            textfont=dict(color="white", size=11),
            cliponaxis=False,
        ))
        fig_top.update_layout(**PT, height=320,
                              xaxis_title="Amount (₹)",
                              margin=dict(t=20,b=20,l=20,r=100))
        st.plotly_chart(fig_top, use_container_width=True)

    st.markdown('<div class="section-header">🕸️ Spending Pattern Radar</div>',
                unsafe_allow_html=True)
    top_cats  = cat.head(6)
    max_spend = top_cats["total_spent"].max()
    norm      = (top_cats["total_spent"] / max_spend * 100).tolist()
    labels    = top_cats["category"].tolist()

    fig_radar = go.Figure(go.Scatterpolar(
        r=norm + [norm[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(0,212,255,0.15)",
        line=dict(color="#00d4ff", width=2),
        marker=dict(color="#00d4ff", size=8),
    ))
    fig_radar.update_layout(
        **PT, height=400,
        polar=dict(
            bgcolor="rgba(10,15,30,0.8)",
            radialaxis=dict(range=[0,100],
                            gridcolor="#1a2744",
                            color="#8892b0"),
            angularaxis=dict(gridcolor="#1a2744",
                             color="#ccd6f6"),
        ),
        margin=dict(t=40,b=40,l=40,r=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 7 — ADD EXPENSE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Expense":
    st.markdown("""
    <div class='hero-card'>
      <h2 style='margin:0;color:#00d4ff'>➕ Add New Expense</h2>
      <p style='color:#8892b0;margin:5px 0 0'>
        Log a new expense to your tracker
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📝 Expense Details</div>',
                    unsafe_allow_html=True)
        date        = st.date_input("📅 Date", datetime.now())
        category    = st.selectbox("📂 Category", [
            "Food","Travel","Shopping",
            "Bills","Entertainment",
            "Health","Education",
            "Groceries","Personal Care","Transport",
        ])
        description = st.text_input("📝 Description",
                                    placeholder="e.g. Zomato order")
        amount      = st.number_input("💰 Amount (₹)",
                                      min_value=0.0,
                                      value=0.0, step=10.0)
        payment     = st.selectbox("💳 Payment Method", [
            "UPI","Credit Card","Debit Card",
            "Cash","Net Banking","Wallet",
        ])

        if st.button("➕ Add Expense", type="primary"):
            if amount > 0 and description:
                csv_path         = "data/expenses.csv"
                current_expenses = pd.read_csv(csv_path)
                new_expense      = pd.DataFrame([{
                    "date":           date.strftime("%Y-%m-%d"),
                    "category":       category,
                    "amount":         amount,
                    "payment_method": payment,
                    "description":    description,
                    "is_essential":   category in [
                        "Food","Bills","Groceries",
                        "Health","Transport","Travel"
                    ],
                    "month":          date.strftime("%Y-%m"),
                }])
                updated = pd.concat(
                    [current_expenses, new_expense],
                    ignore_index=True
                )
                updated.to_csv(csv_path, index=False)
                st.success(
                    f"✅ Added ₹{amount:,.0f} for "
                    f"'{description}' in {category}!"
                )
                st.balloons()
                load_all.clear()
                st.rerun()
            else:
                st.error("❌ Please fill amount and description!")

    with col2:
        st.markdown('<div class="section-header">📋 Recent Expenses</div>',
                    unsafe_allow_html=True)
        recent_df = pd.read_csv("data/expenses.csv")
        recent    = recent_df.sort_values("date", ascending=False).head(15)
        st.dataframe(
            recent[["date","category","description",
                    "amount","payment_method"]],
            use_container_width=True,
            height=400,
        )

    # ── Delete Expense ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🗑️ Delete an Expense</div>',
                unsafe_allow_html=True)

    del_df = pd.read_csv("data/expenses.csv")

    if del_df.empty:
        st.info("No expenses found to delete.")
    else:
        # Build a readable label for each row
        del_df["_label"] = (
            del_df["date"].astype(str) + "  |  " +
            del_df["category"].astype(str) + "  |  " +
            del_df["description"].astype(str) + "  |  ₹" +
            del_df["amount"].astype(str)
        )

        col_d1, col_d2 = st.columns([3, 1])

        with col_d1:
            selected_label = st.selectbox(
                "Select expense to delete",
                del_df["_label"].tolist(),
                index=0,
            )

        with col_d2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", type="primary"):
                # Find the row index matching the selected label
                drop_idx = del_df[del_df["_label"] == selected_label].index
                del_df   = del_df.drop(index=drop_idx).drop(columns=["_label"])
                del_df.to_csv("data/expenses.csv", index=False)
                st.success("✅ Expense deleted successfully!")
                load_all.clear()
                st.rerun()

        # Show selected row as a preview
        preview = del_df[del_df["_label"] == selected_label]
        if not preview.empty:
            r = preview.iloc[0]
            st.markdown(f"""
            <div class="insight-card" style="border-left:4px solid #ff4444">
                📅 <b>{r['date']}</b> &nbsp;|&nbsp;
                📂 <b>{r['category']}</b> &nbsp;|&nbsp;
                📝 {r['description']} &nbsp;|&nbsp;
                💰 <b>₹{r['amount']}</b> &nbsp;|&nbsp;
                💳 {r['payment_method']}
            </div>
            """, unsafe_allow_html=True)
