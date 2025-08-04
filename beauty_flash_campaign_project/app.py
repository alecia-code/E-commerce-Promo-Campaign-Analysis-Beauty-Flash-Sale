import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
df = pd.read_csv("beauty_flash_sale.csv", parse_dates=["timestamp"])

# Initialize app
app = Dash(__name__)
app.title = "Beauty Flash Sale Dashboard"

# Layout
app.layout = html.Div([
    html.H1("💄 Flash Sale Campaign Performance", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Filter by Product Category"),
            dcc.Dropdown(
                options=[{"label": cat, "value": cat} for cat in df["product_category"].unique()],
                id="category-filter",
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by Promo Type"),
            dcc.Dropdown(
                options=[{"label": promo, "value": promo} for promo in df["promo_type"].unique()],
                id="promo-filter",
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Filter by User Segment"),
            dcc.Dropdown(
                options=[{"label": seg, "value": seg} for seg in df["user_segment"].unique()],
                id="segment-filter",
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], style={'padding': '10px'}),

    html.Div(id="kpi-cards", style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '20px'}),

    dcc.Graph(id="time-series"),
    dcc.Graph(id="promo-performance"),
    dcc.Graph(id="fulfillment-heatmap"),
])

# Callbacks
@app.callback(
    [Output("kpi-cards", "children"),
     Output("time-series", "figure"),
     Output("promo-performance", "figure"),
     Output("fulfillment-heatmap", "figure")],
    [Input("category-filter", "value"),
     Input("promo-filter", "value"),
     Input("segment-filter", "value")]
)
def update_dashboard(categories, promos, segments):
    filtered = df.copy()
    if categories:
        filtered = filtered[filtered["product_category"].isin(categories)]
    if promos:
        filtered = filtered[filtered["promo_type"].isin(promos)]
    if segments:
        filtered = filtered[filtered["user_segment"].isin(segments)]

    # KPIs
    total_revenue = filtered["revenue"].sum()
    total_orders = filtered[filtered["conversion"] == 1].shape[0]
    conversion_rate = (total_orders / filtered.shape[0]) * 100 if filtered.shape[0] > 0 else 0
    avg_order_value = filtered["revenue"].sum() / total_orders if total_orders > 0 else 0
    inventory_sold_pct = 100 * (1 - filtered["inventory_remaining"].sum() / (filtered["inventory_remaining"].sum() + total_orders))

    kpis = [
        html.Div([
            html.H4("Total Revenue"),
            html.P(f"${total_revenue:,.2f}")
        ]),
        html.Div([
            html.H4("Conversion Rate"),
            html.P(f"{conversion_rate:.2f}%")
        ]),
        html.Div([
            html.H4("Avg Order Value"),
            html.P(f"${avg_order_value:.2f}")
        ]),
        html.Div([
            html.H4("Orders"),
            html.P(f"{total_orders:,}")
        ]),
        html.Div([
            html.H4("Sell-Through %"),
            html.P(f"{inventory_sold_pct:.1f}%")
        ]),
    ]

    ts_fig = px.line(
        filtered.groupby("date")["revenue"].sum().reset_index(),
        x="date", y="revenue", title="🕒 Revenue Over Time"
    )

    promo_fig = px.bar(
        filtered.groupby("promo_type")["revenue"].sum().reset_index(),
        x="promo_type", y="revenue", title="🎁 Revenue by Promo Type"
    )

    heatmap_df = filtered.groupby(["product_category", "fulfillment_status"]).size().reset_index(name="count")
    heatmap_fig = px.density_heatmap(
        heatmap_df, x="product_category", y="fulfillment_status", z="count",
        color_continuous_scale="Purples", title="📦 Fulfillment Status by Category"
    )

    return kpis, ts_fig, promo_fig, heatmap_fig

# Run server
if __name__ == "__main__":
    app.run_server(debug=True)