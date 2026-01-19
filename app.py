import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Final", layout="wide", initial_sidebar_state="collapsed")

# デザイン設定
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center; min-height: 250px;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; margin-bottom: 2px; }
    .update-time { font-size: 9px; color: #636366; margin-bottom: 5px; }
    .price-val { font-size: 24px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 14px; font-weight: bold; margin-bottom: 8px; }
    .info-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .info-table td { border: 1px solid #3a3a3c; padding: 3px; font-size: 10px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 💡 銘柄リスト（日経時間外とTOPIX先物に予備シンボルを設定）
symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
# 予備の検索候補
alternates = {"NK225E=F": "CME:NIY", "MTI=F": "TOPX"} 

names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

if 'master_store' not in st.session_state:
    st.session_state.master_store = {s: {'p': 0.0, 'v': 0.0, 'h': []} for s in symbols}

def fetch_data(s):
    try:
        t = Ticker(s)
        p_data = t.price[s]
        
        # もしデータが取れず、予備シンボルがある場合はそちらを試す
        if (not p_data or p_data.get('regularMarketPrice') is None) and s in alternates:
            t = Ticker(alternates[s])
            p_data = t.price[alternates[s]]

        curr = p_data.get('regularMarketPrice') or p_data.get('regularMarketPreviousClose') or 0.0
        prev = p_data.get('regularMarketPreviousClose') or curr
        
        if curr > 0: st.session_state.master_store[s]['p'] = curr
        if prev > 0: st.session_state.master_store[s]['v'] = prev
        
        # 履歴取得
        try:
            hist = t.history(period="3d", interval="30m")
            if not hist.empty:
                h_vals = hist.iloc[:, 0].dropna().tolist() # 最初のカラムを取得
                if h_vals: st.session_state.master_store[s]['h'] = h_vals
        except: pass
    except: pass
    return st.session_state.master_store[s]

# 表示
current_time = datetime.now().strftime("%H:%M:%S")
cols = st.columns(3)

# ドル円（計算用）
fx = fetch_data("JPY=X")
fx_rate = fx['p'] or 150.0

for i, s in enumerate(symbols):
    with cols[i % 3]:
        data = fetch_data(s)
        p, v = data['p'], data['v']
        
        # ゴールド換算
        if s == "GC=F" and p > 0:
            p, v = [(val * fx_rate / 31.1035) for val in [p, v]]

        diff = p - v
        pct = (diff / v * 100) if v > 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{flags[i]} {names[i]}</div>
            <div class="update-time">{current_time} 更新</div>
            <div class="price-val">{p:,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        if data['h']:
            fig = go.Figure(data=go.Scatter(y=data['h'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{s}")
        
        st.markdown(f'''<table class="info-table"><tr><td style="background-color:#2c2c2e; width:40%;">終値</td><td style="text-align:right">{v:,.2f}</td></tr></table></div>''', unsafe_allow_html=True)

time.sleep(60)
st.rerun()
