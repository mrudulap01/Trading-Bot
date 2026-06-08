import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging
from datetime import datetime
from typing import Dict, Any, List

from bot.client import BinanceFuturesClient
from bot.orders import OrderService, OrderServiceError
from bot.constants import OrderSide

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Binance Futures Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Comprehensive Custom CSS for Premium SaaS Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Backgrounds */
    .stApp {
        background-color: #0B1220 !important;
        color: #F8FAFC;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Metrics / Cards */
    [data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937;
        padding: 1.5rem !important;
        border-radius: 0.75rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        border-color: #F3BA2F;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        font-family: 'Inter', sans-serif !important;
        margin-top: 0.5rem !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 0.75rem !important;
        overflow: hidden !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        border: 1px solid #1F2937;
    }
    
    /* Primary Buttons (Binance Gold) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F3BA2F 0%, #EAB308 100%) !important;
        color: #111827 !important;
        font-weight: 600 !important;
        border-radius: 0.5rem !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(243, 186, 47, 0.3) !important;
    }

    /* Secondary Buttons */
    .stButton > button[kind="secondary"] {
        background-color: #1F2937 !important;
        color: #F8FAFC !important;
        font-weight: 500 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #374151 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #374151 !important;
        border-color: #4B5563 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111827 !important;
        border-radius: 0.5rem;
        padding: 0.5rem;
        gap: 0.5rem;
        border-bottom: 1px solid #1F2937 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        background-color: transparent !important;
        border-radius: 0.3rem !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1F2937 !important;
        color: #F8FAFC !important;
        border-bottom: 2px solid #F3BA2F !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #0B1220 !important;
        color: #F8FAFC !important;
        border: 1px solid #374151 !important;
        border-radius: 0.5rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #F3BA2F !important;
        box-shadow: 0 0 0 1px #F3BA2F !important;
    }

    /* Custom Cards HTML injection styling */
    .custom-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    .custom-card-header {
        color: #94A3B8;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .custom-card-value {
        color: #F8FAFC;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Status Badges */
    .badge-success { background-color: rgba(34, 197, 94, 0.1); color: #22C55E; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(34, 197, 94, 0.2); }
    .badge-warning { background-color: rgba(243, 186, 47, 0.1); color: #F3BA2F; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(243, 186, 47, 0.2); }
    .badge-danger { background-color: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge-info { background-color: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.2); }

    /* Divider */
    hr {
        border-color: #1F2937 !important;
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# BACKEND INITIALIZATION (CACHED)
# ==========================================
@st.cache_resource
def get_order_service() -> OrderService:
    """Initializes and caches the OrderService to avoid re-auth."""
    client = BinanceFuturesClient()
    return OrderService(client)

def serialize_order(order: Any) -> Dict[str, Any]:
    """Safely converts OrderResponse dataclass (with Enums) into a plain dict."""
    return {
        k: (v.value if hasattr(v, 'value') else v)
        for k, v in vars(order).items()
    }

# ==========================================
# HELPER DATA LOADERS
# ==========================================
@st.cache_data(ttl=60)
def fetch_klines(_order_service: OrderService, symbol: str, interval: str, limit: int) -> List[List[Any]]:
    return _order_service.get_klines(symbol, interval=interval, limit=limit)

@st.cache_data(ttl=15)
def fetch_price(_order_service: OrderService, symbol: str) -> float:
    return _order_service.get_current_price(symbol)

@st.cache_data(ttl=30)
def fetch_open_orders(_order_service: OrderService, symbol: str = None) -> List[Any]:
    return _order_service.get_open_orders(symbol)

@st.cache_data(ttl=30)
def fetch_order_history(_order_service: OrderService, symbol: str, limit: int) -> List[Any]:
    return _order_service.get_order_history(symbol, limit=limit)


# ==========================================
# MAIN APPLICATION
# ==========================================
def main() -> None:
    # Attempt Backend Connection
    try:
        order_service = get_order_service()
    except Exception as e:
        st.error(f"FATAL ERROR: Failed to initialize Binance client: {e}")
        st.stop()

    # ==========================================
    # SIDEBAR
    # ==========================================
    st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #F3BA2F; margin-bottom: 0;">⚡ Binance</h1>
            <h4 style="color: #F8FAFC; margin-top: 0;">Futures Terminal</h4>
            <span class="badge-warning">v1.0.0-testnet</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("NAVIGATION", [
        "📊 Dashboard",
        "⚡ Trade",
        "📋 Open Orders",
        "🕰️ Order History",
        "📈 Analytics",
        "⚙️ Settings"
    ], label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    
    # User Status in Sidebar
    st.sidebar.markdown("""
        <div class="custom-card" style="padding: 1rem; margin-top: 2rem;">
            <div style="color: #94A3B8; font-size: 0.8rem; margin-bottom: 0.5rem;">CONNECTION</div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="height: 8px; width: 8px; background-color: #22C55E; border-radius: 50%; display: inline-block;"></span>
                <span style="color: #F8FAFC; font-weight: 500;">API Connected</span>
            </div>
            <div style="color: #94A3B8; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0.5rem;">SERVER TIME</div>
            <div style="color: #F8FAFC; font-weight: 500;">""" + datetime.now().strftime('%H:%M:%S UTC') + """</div>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # HERO SECTION
    # ==========================================
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding: 1rem 1.5rem; background-color: #111827; border-radius: 0.75rem; border: 1px solid #1F2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);">
            <div>
                <h2 style="margin: 0; color: #F8FAFC;">Live Trading Dashboard</h2>
                <div style="color: #94A3B8; font-size: 0.9rem;">Connected to Binance Futures Testnet</div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <span class="badge-success">API Connected</span>
                <span class="badge-warning">Testnet Mode</span>
                <span class="badge-info">Logging Enabled</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


    # ==========================================
    # PAGE 1: DASHBOARD
    # ==========================================
    if page == "📊 Dashboard":
        
        # Primary Symbol Select
        col_sym, _ = st.columns([2, 8])
        primary_symbol = col_sym.selectbox("Asset", ["BTCUSDT", "ETHUSDT", "BNBUSDT"], index=0, label_visibility="collapsed")
        
        # 1. TOP METRICS PANEL
        try:
            with st.spinner("Loading live metrics..."):
                price = fetch_price(order_service, primary_symbol)
                open_orders = fetch_open_orders(order_service)
                recent_history = fetch_order_history(order_service, primary_symbol, 100)
                
                # Compute metrics
                filled_orders = [o for o in recent_history if o.status.value == "FILLED"]
                vol = sum(o.quantity for o in filled_orders)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(f"{primary_symbol} Price", f"${price:,.2f}" if price else "N/A")
                col2.metric("Open Orders", len(open_orders))
                col3.metric("Recent Fills", len(filled_orders))
                col4.metric("24h Volume (Qty)", f"{vol:,.3f}")
        except Exception as e:
            st.error(f"Failed to fetch market data: {e}")
            return
            
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. WIDGETS ROW (CHART & ACTIVITY)
        c_left, c_right = st.columns([7, 3])
        
        with c_left:
            st.markdown('<div class="custom-card-header">📈 Live Chart</div>', unsafe_allow_html=True)
            try:
                klines = fetch_klines(order_service, primary_symbol, "1h", 100)
                df_k = pd.DataFrame(klines, columns=['time','open','high','low','close','vol','ctime','qvol','trades','tbbav','tbqav','ignore'])
                df_k['time'] = pd.to_datetime(df_k['time'], unit='ms')
                df_k = df_k.astype({'open': float, 'high': float, 'low': float, 'close': float, 'vol': float})
                
                fig = go.Figure(data=[go.Candlestick(
                    x=df_k['time'],
                    open=df_k['open'],
                    high=df_k['high'],
                    low=df_k['low'],
                    close=df_k['close'],
                    increasing_line_color='#22C55E', 
                    decreasing_line_color='#EF4444'
                )])
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=0, r=0, t=10, b=0),
                    xaxis_rangeslider_visible=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94A3B8')
                )
                
                # Wrap chart in styled container
                st.markdown('<div style="background-color: #111827; border: 1px solid #1F2937; border-radius: 0.75rem; padding: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.warning("Chart data temporarily unavailable.")

        with c_right:
            st.markdown('<div class="custom-card-header">⚡ Recent Activity</div>', unsafe_allow_html=True)
            
            if recent_history:
                df_recent = pd.DataFrame([serialize_order(o) for o in recent_history[:5]])
                df_recent = df_recent[['side', 'type', 'quantity', 'status']]
                
                def highlight_status(val):
                    color = '#22C55E' if val == 'FILLED' else '#F3BA2F' if val == 'NEW' else '#EF4444'
                    return f'color: {color}; font-weight: bold'
                
                st.dataframe(df_recent.style.map(highlight_status, subset=['status']), use_container_width=True, hide_index=True)
            else:
                st.info("No recent orders.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div class="custom-card">
                    <div class="custom-card-header">WALLET BALANCE</div>
                    <div class="custom-card-value">$10,000.00 <span style="font-size: 1rem; color: #94A3B8; font-weight: normal;">USDT</span></div>
                    <div style="color: #3B82F6; font-size: 0.8rem; margin-top: 0.5rem;">Mocked for Testnet environment</div>
                </div>
            """, unsafe_allow_html=True)


    # ==========================================
    # PAGE 2: TRADE TERMINAL
    # ==========================================
    elif page == "⚡ Trade":
        
        c_form, c_preview = st.columns([6, 4])
        
        with c_form:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="custom-card-header">📝 Order Entry</div>', unsafe_allow_html=True)
            
            col_s1, col_s2 = st.columns(2)
            symbol = col_s1.text_input("Trading Pair", value="BTCUSDT").upper()
            
            try:
                current_price = fetch_price(order_service, symbol) if symbol else 0.0
            except:
                current_price = 0.0
                
            col_s2.markdown(f"""
                <div style="margin-top: 1.8rem; font-size: 1.1rem; color: #94A3B8;">
                    Market Price: <span style="color: #F3BA2F; font-weight: bold;">${current_price:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Streamlit Tabs for Order Types
            tab_market, tab_limit, tab_stop = st.tabs(["Market", "Limit", "Stop Limit"])
            
            submit_type = None
            side_input = None
            qty_input = 0.0
            price_input = None
            stop_input = None
            
            with tab_market:
                with st.form("market_form", border=False):
                    col1, col2 = st.columns(2)
                    side_m = col1.selectbox("Side", ["BUY", "SELL"], key="m_side")
                    qty_m = col2.number_input("Quantity", min_value=0.001, step=0.001, format="%.3f", key="m_qty")
                    if st.form_submit_button("Execute Market Order", type="primary", use_container_width=True):
                        submit_type, side_input, qty_input = "MARKET", side_m, qty_m
            
            with tab_limit:
                with st.form("limit_form", border=False):
                    col1, col2 = st.columns(2)
                    side_l = col1.selectbox("Side", ["BUY", "SELL"], key="l_side")
                    qty_l = col2.number_input("Quantity", min_value=0.001, step=0.001, format="%.3f", key="l_qty")
                    price_l = st.number_input("Limit Price", min_value=0.01, step=10.0, value=current_price, key="l_price")
                    if st.form_submit_button("Place Limit Order", type="primary", use_container_width=True):
                        submit_type, side_input, qty_input, price_input = "LIMIT", side_l, qty_l, price_l

            with tab_stop:
                with st.form("stop_form", border=False):
                    col1, col2 = st.columns(2)
                    side_s = col1.selectbox("Side", ["BUY", "SELL"], key="s_side")
                    qty_s = col2.number_input("Quantity", min_value=0.001, step=0.001, format="%.3f", key="s_qty")
                    price_s = st.number_input("Limit Price", min_value=0.01, step=10.0, value=current_price, key="s_price")
                    stop_s = st.number_input("Stop Price Trigger", min_value=0.01, step=10.0, value=current_price, key="s_stop")
                    if st.form_submit_button("Place Stop Limit", type="primary", use_container_width=True):
                        submit_type, side_input, qty_input, price_input, stop_input = "STOP_LIMIT", side_s, qty_s, price_s, stop_s
                        
            st.markdown('</div>', unsafe_allow_html=True)

        with c_preview:
            # Order Preview logic
            preview_price = price_input if submit_type in ["LIMIT", "STOP_LIMIT"] else current_price
            # If form hasn't been submitted, just show mock estimate
            est_cost = (preview_price or 0) * (qty_input or 0.001)
            
            risk_color = "#22C55E" if side_input == "BUY" else "#EF4444"
            risk_text = "Long Exposure" if side_input == "BUY" else "Short Exposure"
            
            st.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-header">🔍 Order Preview</div>
                    <div style="margin-top: 1.5rem; display: flex; justify-content: space-between; border-bottom: 1px solid #1F2937; padding-bottom: 0.5rem;">
                        <span style="color: #94A3B8;">Estimated Position Value</span>
                        <span style="color: #F8FAFC; font-weight: bold; font-size: 1.2rem;">${est_cost:,.2f}</span>
                    </div>
                    <div style="margin-top: 1rem; display: flex; justify-content: space-between; border-bottom: 1px solid #1F2937; padding-bottom: 0.5rem;">
                        <span style="color: #94A3B8;">Risk Indicator</span>
                        <span style="color: {risk_color}; font-weight: bold;">{risk_text}</span>
                    </div>
                    <div style="margin-top: 1rem; color: #94A3B8; font-size: 0.85rem; line-height: 1.5;">
                        <i style="color: #F3BA2F;">Note:</i> Market orders execute at the best available price and may experience slippage. Always ensure sufficient margin.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if submit_type:
                try:
                    with st.spinner("Transmitting to Exchange..."):
                        if submit_type == "MARKET":
                            res = order_service.place_market_order(symbol, OrderSide(side_input), qty_input)
                        elif submit_type == "LIMIT":
                            res = order_service.place_limit_order(symbol, OrderSide(side_input), qty_input, price_input)
                        elif submit_type == "STOP_LIMIT":
                            res = order_service.place_stop_limit_order(symbol, OrderSide(side_input), qty_input, price_input, stop_input)
                        
                        st.success(f"✅ {submit_type} Order Executed!")
                        st.json(serialize_order(res))
                        fetch_open_orders.clear()
                        fetch_order_history.clear()
                        
                except OrderServiceError as e:
                    st.error(f"❌ Execution Rejected: {e}")
                except ValueError as e:
                    st.error(f"❌ Validation Failed: {e}")

    # ==========================================
    # PAGE 3: OPEN ORDERS
    # ==========================================
    elif page == "📋 Open Orders":
        
        c1, c2 = st.columns([8, 2])
        symbol_filter = c1.text_input("Filter by Symbol", placeholder="e.g. BTCUSDT", label_visibility="collapsed").upper()
        if c2.button("🔄 Refresh Data", type="primary", use_container_width=True):
            fetch_open_orders.clear()
            
        with st.spinner("Fetching order book..."):
            try:
                orders = fetch_open_orders(order_service, symbol_filter if symbol_filter else None)
                if not orders:
                    st.markdown("""
                        <div style="text-align: center; padding: 4rem; background-color: #111827; border-radius: 0.75rem; border: 1px dashed #374151;">
                            <h3 style="color: #94A3B8;">No Open Orders Found</h3>
                            <p style="color: #4B5563;">Your order book is currently clear.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    df = pd.DataFrame([serialize_order(o) for o in orders])
                    
                    for index, row in df.iterrows():
                        side_color = "#22C55E" if row['side'] == 'BUY' else "#EF4444"
                        st.markdown(f"""
                            <div style="background-color: #111827; border: 1px solid #1F2937; border-left: 4px solid {side_color}; border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; gap: 2rem; align-items: center;">
                                    <div style="font-weight: 700; font-size: 1.1rem; color: #F8FAFC;">{row['symbol']}</div>
                                    <div style="color: {side_color}; font-weight: 600;">{row['side']}</div>
                                    <div style="color: #94A3B8;">{row['type']}</div>
                                    <div style="color: #F8FAFC;"><span style="color: #94A3B8;">Qty:</span> {row['quantity']}</div>
                                    <div style="color: #F3BA2F;"><span style="color: #94A3B8;">Price:</span> ${row['price']}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Cancel Button (needs to be native ST to handle Python callbacks)
                        if st.button(f"Cancel Order {row['order_id']}", key=f"cancel_{row['order_id']}", type="secondary"):
                            try:
                                order_service.cancel_order(row['symbol'], int(row['order_id']))
                                st.success(f"Order {row['order_id']} canceled!")
                                fetch_open_orders.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to cancel: {e}")
                                
                    st.markdown("<br><h4>Raw Data View</h4>", unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error fetching open orders: {e}")

    # ==========================================
    # PAGE 4: ORDER HISTORY
    # ==========================================
    elif page == "🕰️ Order History":
        
        c1, c2, c3 = st.columns([4, 4, 2])
        symbol = c1.text_input("Symbol", value="BTCUSDT").upper()
        limit = c2.number_input("Lookback Limit", min_value=1, max_value=1000, value=50)
        
        if c3.button("Load Ledger", type="primary", use_container_width=True):
            fetch_order_history.clear()
            
        if symbol:
            try:
                with st.spinner("Loading ledger..."):
                    orders = fetch_order_history(order_service, symbol, int(limit))
                
                if not orders:
                    st.info("No historical records found.")
                else:
                    df = pd.DataFrame([serialize_order(o) for o in orders])
                    
                    cf1, cf2 = st.columns(2)
                    status_filter = cf1.multiselect("Filter Status", df['status'].unique(), default=df['status'].unique())
                    side_filter = cf2.multiselect("Filter Side", df['side'].unique(), default=df['side'].unique())
                    
                    df_filtered = df[(df['status'].isin(status_filter)) & (df['side'].isin(side_filter))]
                    
                    def highlight_ledger(val):
                        if val == 'FILLED': return 'color: #22C55E; font-weight: bold'
                        if val == 'NEW': return 'color: #F3BA2F; font-weight: bold'
                        return 'color: #EF4444; font-weight: bold'
                        
                    st.dataframe(df_filtered.style.map(highlight_ledger, subset=['status']), use_container_width=True, hide_index=True)
                    
                    csv = df_filtered.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Export Ledger to CSV",
                        data=csv,
                        file_name=f"{symbol}_order_history.csv",
                        mime="text/csv",
                        type="secondary"
                    )
            except Exception as e:
                st.error(f"Error loading ledger: {e}")

    # ==========================================
    # PAGE 5: ANALYTICS
    # ==========================================
    elif page == "📈 Analytics":
        
        symbol = st.text_input("Analyze Symbol", value="BTCUSDT").upper()
        
        if symbol:
            try:
                orders = fetch_order_history(order_service, symbol, 1000)
                if not orders:
                    st.warning("Not enough data to run analytics.")
                else:
                    df = pd.DataFrame([serialize_order(o) for o in orders])
                    
                    # Top KPI Cards
                    df_filled = df[df['status'] == 'FILLED']
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Executed Volume", f"{df_filled['quantity'].sum():.4f}")
                    c2.metric("Total Buy Orders", len(df[df['side'] == 'BUY']))
                    c3.metric("Total Sell Orders", len(df[df['side'] == 'SELL']))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    c_chart1, c_chart2 = st.columns(2)
                    
                    with c_chart1:
                        st.markdown('<div class="custom-card-header">Distribution by Status</div>', unsafe_allow_html=True)
                        status_counts = df['status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Count']
                        fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.5,
                                         color='Status', color_discrete_map={'FILLED':'#22C55E', 'NEW':'#F3BA2F', 'CANCELED':'#EF4444', 'REJECTED':'#EF4444'})
                        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
                        
                        st.markdown('<div style="background-color: #111827; border: 1px solid #1F2937; border-radius: 0.75rem; padding: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with c_chart2:
                        st.markdown('<div class="custom-card-header">Filled Volumes</div>', unsafe_allow_html=True)
                        if not df_filled.empty:
                            fig_bar = px.bar(df_filled, x='order_id', y='quantity', color='side', 
                                             color_discrete_map={'BUY':'#22C55E', 'SELL':'#EF4444'})
                            fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94A3B8'))
                            
                            st.markdown('<div style="background-color: #111827; border: 1px solid #1F2937; border-radius: 0.75rem; padding: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
                            st.plotly_chart(fig_bar, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("No filled orders to analyze volume.")

            except Exception as e:
                st.error(f"Analytics failure: {e}")

    # ==========================================
    # PAGE 6: SETTINGS
    # ==========================================
    elif page == "⚙️ Settings":
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("""
                <div class="custom-card">
                    <div class="custom-card-header">🔧 Environment Configuration</div>
                    <div style="margin-top: 1rem; color: #94A3B8;">Target Network: <span style="color: #F8FAFC; float: right;">Binance Futures Testnet</span></div>
                    <div style="margin-top: 1rem; color: #94A3B8;">Testnet Enabled: <span style="color: #22C55E; float: right; font-weight: bold;">TRUE</span></div>
                    <div style="margin-top: 1rem; color: #94A3B8;">Log Level: <span style="color: #3B82F6; float: right;">INFO</span></div>
                    <div style="margin-top: 1rem; color: #94A3B8;">UI Framework: <span style="color: #F8FAFC; float: right;">Streamlit + Custom CSS</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
                <div class="custom-card">
                    <div class="custom-card-header">🔐 Security Verification</div>
                    <div style="color: #94A3B8; margin-top: 1rem; margin-bottom: 1rem;">
                        Verify your API keys and permissions securely without placing orders.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Ping API Keys & Validate Permissions", type="primary", use_container_width=True):
                with st.spinner("Authenticating..."):
                    status = order_service.client.verify_credentials()
                
                if status['api_key_valid'] and status['secret_key_valid']:
                    st.success("✅ API Keys Validated Successfully.")
                else:
                    st.error("❌ API Keys Rejected by Binance.")
                    
                if status['futures_permissions']:
                    st.success("✅ Futures Permissions Confirmed.")
                else:
                    st.error("❌ Futures Account Missing or Disabled.")

if __name__ == "__main__":
    main()
