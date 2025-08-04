import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("beauty_flash_sale.csv", parse_dates=["timestamp"])

st.set_page_config(page_title="Beauty Flash Sale Dashboard", layout="wide")

st.title("💄 Flash Sale Campaign Performance")

# Sidebar filters
with st.sidebar:
    st.header("Filter Data")
    selected_category = st.multiselect("Product Category", options=df["product_category"].unique(), default=df["product_category"].unique())
    selected_promo = st.multiselect("Promo Type", options=df["promo_type"].unique(), default=df["promo_type"].unique())
    selected_segment = st.multiselect("User Segment", options=df["user_segment"].unique(), default=df["user_segment"].unique())

# Apply filters
filtered = df[
    df["product_category"].isin(selected_category) &
    df["promo_type"].isin(selected_promo) &
    df["user_segment"].isin(selected_segment)
]

# KPI calculations
total_revenue = filtered["revenue"].sum()
total_orders = filtered[filtered["conversion"] == 1].shape[0]
conversion_rate = (total_orders / filtered.shape[0]) * 100 if filtered.shape[0] > 0 else 0
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
inventory_sold_pct = 100 * (1 - filtered["inventory_remaining"].sum() / (filtered["inventory_remaining"].sum() + total_orders))

# KPI display
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Conversion Rate", f"{conversion_rate:.2f}%")
col3.metric("Avg Order Value", f"${avg_order_value:.2f}")
col4.metric("Orders", f"{total_orders:,}")
col5.metric("Sell-Through %", f"{inventory_sold_pct:.1f}%")

# Charts
st.subheader("📈 Revenue Over Time")
revenue_time = filtered.groupby(filtered["timestamp"].dt.date)["revenue"].sum().reset_index()
fig1 = px.line(revenue_time, x="timestamp", y="revenue", title="Revenue Over Time")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("🎁 Revenue by Promo Type")
promo_rev = filtered.groupby("promo_type")["revenue"].sum().reset_index()
fig2 = px.bar(promo_rev, x="promo_type", y="revenue", title="Revenue by Promo Type")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📦 Fulfillment Status by Category")
heatmap_df = filtered.groupby(["product_category", "fulfillment_status"]).size().reset_index(name="count")
fig3 = px.density_heatmap(heatmap_df, x="product_category", y="fulfillment_status", z="count",
                          color_continuous_scale="Purples", title="Fulfillment Status Heatmap")
st.plotly_chart(fig3, use_container_width=True)