import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Max", layout="wide", initial_sidebar_state="collapsed")

# 背景・デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center; min-height: 250px;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; margin-bottom: 2px; }
    .price-val { font-size: 26px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 14px; font-weight: bold; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 💡 裏ルート：日本市場で取れない銘柄は、シカゴ市場(CME)等のシンボルで代用
# 日経時間外（NK225E=F）→ CME日経先物（NIY=F）
# TOPIX先物（MTI=F）→ TOPIX（1306.T）
symbols = ["^N225", "NIY=F", "NIY=F", "1306.T", "1306.T", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]

if 'p_store' not in st.session_state:
    st.session_state.p_store = {s: {'p': 0.0, 'v': 0.0, 'h': []} for s in symbols}

def fetch_pro(s):
    try:
        t = Ticker(s)
        # 💡 価格取得（複数候補から一番マシな値を探す）
        p_info = t.price[s]
        curr = p_info.get('regularMarketPrice') or p_info.get('preMarketPrice') or p_info.get('regularMarketPreviousClose') or 0.0
        prev = p_info.get('regularMarketPreviousClose') or curr
        
        if curr > 0: st.session_state.p_store[s]['p'] = curr
        if prev > 0: st.session_state.p_store[s]['v'] = prev

        # 💡 グラフ取得
        try:
            h = t.history(period="3d", interval="30m")
            if not h.empty:
                vals = h.iloc[:, 0].dropna().tolist()
                if vals: st.session_state.p_store[s]['h'] = vals
        except: pass
    except: pass
    return st.session_state.p_store[s]

# 表示
cur_time = datetime.now().strftime("%H:%M:%S")
cols = st.columns(3)
fx_val = fetch_pro("JPY=X")['p'] or 150.0

for i, s in enumerate(symbols):
    with cols[i % 3]:
        d = fetch_pro(s)
        p, v = d['p'], d['v']
        
        if s == "GC=F" and p > 0:
            p, v = [(x * fx_val / 31.1035) for x in [p, v]]

        diff = p - v
        pct = (diff / v * 100) if v > 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        # 特殊：TOPIX先物(1306.T)を表示する時だけ名前を戻す
        display_name = names[i]

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{display_name}</div>
            <div style="font-size: 9px; color: #636366;">{cur_time} Update</div>
            <div class="price-val">{p:,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        if d['h']:
            fig = go.Figure(data=go.Scatter(y=d['h'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"k_{i}")

time.sleep(60)
st.rerun()
