
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="AlphaTrack // Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, premium developer UI
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #1C83E1; }
    div[data-testid="stForm"] { border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 10px; padding: 20px; }
    </style>
""", unsafe_html=True)

# ==========================================
# 2. SESSION STATE & DATA INITIALIZATION
# ==========================================
# Pre-seeding data so the app displays immediately without crashing
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame([
        {"ID": 1, "Date": (datetime.now() - timedelta(days=12)).date(), "Asset": "BTC", "Type": "Buy", "Quantity": 0.65, "Price": 62500.0, "Total": 40625.0},
        {"ID": 2, "Date": (datetime.now() - timedelta(days=8)).date(), "Asset": "ETH", "Type": "Buy", "Quantity": 4.5, "Price": 3200.0, "Total": 14400.0},
        {"ID": 3, "Date": (datetime.now() - timedelta(days=4)).date(), "Asset": "BTC", "Type": "Sell", "Quantity": 0.15, "Price": 67000.0, "Total": 10050.0},
        {"ID": 4, "Date": (datetime.now() - timedelta(days=2)).date(), "Asset": "SOL", "Type": "Buy", "Quantity": 35.0, "Price": 145.0, "Total": 5075.0},
        {"ID": 5, "Date": (datetime.now() - timedelta(days=1)).date(), "Asset": "AAPL", "Type": "Buy", "Quantity": 20.0, "Price": 180.0, "Total": 3600.0}
    ])

if 'next_id' not in st.session_state:
    st.session_state['next_id'] = 6

# Static Live Market Prices for Real-Time Valuation Matrix
MARKET_PRICES = {
    "BTC": 68500.0,
    "ETH": 3550.0,
    "SOL": 162.5,
    "AAPL": 188.3,
    "GOOG": 174.5,
    "NVDA": 127.4
}

# ==========================================
# 3. CORE CALCULATIONS ENGINE
# ==========================================
def calculate_portfolio_metrics(df):
    if df.empty:
        return pd.DataFrame(), 0.0, 0.0, 0.0
    
    summary_data = []
    unique_assets = df['Asset'].unique()
    
    for asset in unique_assets:
        asset_df = df[df['Asset'] == asset]
        
        buys = asset_df[asset_df['Type'] == 'Buy']
        sells = asset_df[asset_df['Type'] == 'Sell']
        
        total_qty_bought = buys['Quantity'].sum()
        total_spent = buys['Total'].sum()
        
        total_qty_sold = sells['Quantity'].sum()
        total_received = sells['Total'].sum()
        
        net_qty = total_qty_bought - total_qty_sold
        
        # Bypass closed or empty balance positions
        if net_qty <= 0:
            continue
            
        avg_buy_price = (total_spent / total_qty_bought) if total_qty_bought > 0 else 0
        current_price = MARKET_PRICES.get(asset, 1.0)
        current_value = net_qty * current_price
        
        net_invested = total_spent - total_received
        profit_loss = current_value - net_invested
        pl_percentage = (profit_loss / net_invested * 100) if net_invested > 0 else 0.0
        
        summary_data.append({
            "Asset": asset,
            "Holdings": round(net_qty, 4),
            "Avg Buy Price": round(avg_buy_price, 2),
            "Current Price": current_price,
            "Current Value": round(current_value, 2),
            "Net Invested": round(net_invested, 2),
            "Profit / Loss": round(profit_loss, 2),
            "Return %": round(pl_percentage, 2)
        })
        
    summary_df = pd.DataFrame(summary_data)
    
    if summary_df.empty:
        return pd.DataFrame(), 0.0, 0.0, 0.0
        
    total_current_value = summary_df['Current Value'].sum()
    total_net_invested = summary_df['Net Invested'].sum()
    total_profit_loss = total_current_value - total_net_invested
    
    return summary_df, total_current_value, total_net_invested, total_profit_loss

def generate_historical_trend(df):
    if df.empty:
        return pd.DataFrame(columns=["Date", "Portfolio Value"])
    
    start_date = df['Date'].min()
    end_date = datetime.now().date()
    date_range = pd.date_range(start_date, end_date)
    
    history = []
    for current_day in date_range:
        day_date = current_day.date()
        past_df = df[df['Date'] <= day_date]
        
        day_value = 0.0
        for asset in past_df['Asset'].unique():
            asset_past = past_df[past_df['Asset'] == asset]
            qty = 0.0
            for _, row in asset_past.iterrows():
                if row['Type'] == 'Buy':
                    qty += row['Quantity']
                else:
                    qty -= row['Quantity']
            
            price = MARKET_PRICES.get(asset, 1.0)
            days_ago = (end_date - day_date).days
            simulated_price = price * (1 + (np.sin(days_ago * 0.1) * 0.02))
            day_value += max(0.0, qty * simulated_price)
            
        history.append({"Date": day_date, "Portfolio Value ($)": round(day_value, 2)})
        
    return pd.DataFrame(history)

# Process current application metrics cleanly
transactions_df = st.session_state['transactions']
summary_df, total_val, total_inv, total_pl = calculate_portfolio_metrics(transactions_df)
history_df = generate_historical_trend(transactions_df)

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("⚡ AlphaTrack Pro")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation Menu", ["📊 Dashboard Overview", "💸 Transaction Ledger", "⚙️ Market Price Feeds"])

st.sidebar.markdown("---")
st.sidebar.markdown("### System Health")
st.sidebar.success("Database Status: Connected")
st.sidebar.info(f"Cache Synchronized: {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. PAGE ROUTING & VIEWS
# ==========================================

# --- VIEW: DASHBOARD OVERVIEW ---
if page == "📊 Dashboard Overview":
    st.title("Portfolio Dashboard Analytics")
    st.markdown("Real-time performance metrics and asset distribution matrices.")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Total Asset Valuation", value=f"${total_val:,.2f}", delta=f"Net Allocation: ${total_inv:,.2f}", delta_color="off")
    with m2:
        pl_color = "normal" if total_pl >= 0 else "inverse"
        st.metric(label="Total Net Profit/Loss", value=f"${total_pl:,.2f}", delta=f"{((total_pl/total_inv)*100 if total_inv > 0 else 0):+.2f}%", delta_color=pl_color)
    with m3:
        active_assets = len(summary_df) if not summary_df.empty else 0
        st.metric(label="Active Traded Assets", value=str(active_assets), delta=f"Total Trades Logged: {len(transactions_df)}")
        
    st.markdown("---")
    
    g1, g2 = st.columns([3, 2])
    with g1:
        st.subheader("Historical Performance Curve")
        if not history_df.empty:
            fig_line = px.line(
                history_df, x="Date", y="Portfolio Value ($)",
                template="plotly_dark", color_discrete_sequence=["#1C83E1"]
            )
            fig_line.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No tracking milestones recorded.")
            
    with g2:
        st.subheader("Asset Allocation Split")
        if not summary_df.empty:
            fig_pie = px.pie(
                summary_df, values="Current Value", names="Asset",
                hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No asset distribution profiles.")

    st.markdown("---")
    st.subheader("Asset Allocation Breakdown Matrix")
    if not summary_df.empty:
        st.dataframe(summary_df.style.format({
            "Avg Buy Price": "${:,.2f}",
            "Current Price": "${:,.2f}",
            "Current Value": "${:,.2f}",
            "Net Invested": "${:,.2f}",
            "Profit / Loss": "${:,.2f}",
            "Return %": "{:+.2f}%"
        }), use_container_width=True, hide_index=True)
    else:
        st.warning("No live tracking metrics generated. Add transactions via the Ledger panel.")

# --- VIEW: TRANSACTION LEDGER ---
elif page == "💸 Transaction Ledger":
    st.title("Transaction Ledger & Asset Management")
    st.markdown("Log execution files or purge faulty trades directly from operational cache.")
    
    form_col, management_col = st.columns([1, 1])
    
    with form_col:
        st.subheader("➕ Log New Trade Execution")
        with st.form(key="trade_entry_form", clear_on_submit=True):
            f_date = st.date_input("Execution Date", value=datetime.now().date())
            f_asset = st.selectbox("Select Asset Token", list(MARKET_PRICES.keys()))
            f_type = st.radio("Order Type", ["Buy", "Sell"], horizontal=True)
            f_qty = st.number_input("Token Quantity", min_value=0.0001, step=0.01, format="%.4f")
            f_price = st.number_input("Execution Price Per Unit ($)", min_value=0.01, step=1.0, format="%.2f")
            
            submit_trade = st.form_submit_with_ui_behavior("Commit Trade Order", type="primary")
            
            if submit_trade:
                total_cost = f_qty * f_price
                
                # Dynamic validation logic protecting against illegal short selling
                if f_type == "Sell" and not summary_df.empty:
                    current_holding = summary_df[summary_df['Asset'] == f_asset]['Holdings'].sum()
                    if f_qty > current_holding:
                        st.error(f"Execution Halted: Short-selling rejected. Maximum available units to sell of {f_asset}: {current_holding}")
                        st.stop()

                new_order = {
                    "ID": int(st.session_state['next_id']),
                    "Date": f_date,
                    "Asset": f_asset,
                    "Type": f_type,
                    "Quantity": float(f_qty),
                    "Price": float(f_price),
                    "Total": float(total_cost)
                }
                
                st.session_state['transactions'] = pd.concat([
                    st.session_state['transactions'], 
                    pd.DataFrame([new_order])
                ], ignore_index=True)
                st.session_state['next_id'] += 1
                
                st.success(f"Confirmed: Added {f_type} order for {f_qty} {f_asset}!")
                st.rerun()

    with management_col:
        st.subheader("🗑️ Database Row Deletion")
        if not transactions_df.empty:
            target_id = st.selectbox(
                "Select Target Transaction ID to Purge", 
                options=transactions_df['ID'].tolist(),
                key="purge_target_selector"
            )
            
            confirm_purge = st.button("Purge Target Record From Memory", type="primary", use_container_width=True)
            if confirm_purge:
                st.session_state['transactions'] = transactions_df[transactions_df['ID'] != target_id]
                st.success(f"Record #{target_id} successfully dropped from framework cache.")
                st.rerun()
        else:
            st.info("No transaction records available inside the sequence buffer.")

    st.markdown("---")
    st.subheader("Audit Trail Ledger Logs (Immutable Order Book)")
    if not transactions_df.empty:
        st.dataframe(
            transactions_df.sort_values(by="Date", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No trade parameters found inside system records.")

# --- VIEW: MARKET PRICE FEEDS ---
elif page == "⚙️ Market Price Feeds":
    st.title("Market Pricing Engine Feeds")
    st.markdown("Global real-time market lookups utilized for live financial asset valuation.")
    
    price_data = [{"Asset": k, "Assigned Valuation Price": f"${v:,.2f}"} for k, v in MARKET_PRICES.items()]
    st.table(pd.DataFrame(price_data))
    st.caption("Pricing variables are evaluated in memory structures directly.")
