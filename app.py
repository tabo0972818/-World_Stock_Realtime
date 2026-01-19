import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Fix", layout="wide", initial_sidebar_state="collapsed")

# 漆黒のデザイン
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 15px; 
        background-color: #1c1c1e; margin-bottom: 12px; text-align: center; min-height: 200px;
    }
    .stock-name { font-size: 14px; font-weight: bold; color: #8e8e93; margin-bottom: 5px; }
    .price-val { font-size: 32px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# あなたが指定した8銘柄を確実に表示
config = [
    {"name": "日経平均", "symbol": "^N225"},
    {"name": "日経先物", "symbol": "NIY=F"},
    {"name": "日経時間外", "symbol": "NIY=F"},
    {"name": "TOPIX", "symbol": "1306.T"},
    {"name": "TOPIX先物", "symbol": "1306.T"},
    {"name": "ドル円", "symbol": "JPY=X"},
    {"name": "ゴールド(円/g)", "symbol": "GC=F"},
    {"name": "BTC(円)", "symbol": "BTC-JPY"}
]

if 'cache' not in st.session_state:
    st.session_state.cache = {c['name']: {'p': 0.0, 'v': 0.0, 'h': []} for c in config}

def get_data(name, symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        curr = info['last_price']
        prev = info['previous_close']
        
        if curr > 0: st.session_state.cache[name]['p'] = curr
        if prev > 0: st.session_state.cache[name]['v'] = prev

        try:
            h = t.history(period="3d", interval="30m")
            if not h.empty:
                st.session_state.cache[name]['h'] = h['Close'].dropna().tolist()
        except: pass
    except: pass
    return st.session_state.cache[name]

# 描画
ut = datetime.now().strftime("%H:%M:%S")
fx = get_data("ドル円", "JPY=X")['p'] or 150.0
cols = st.columns(2)

for i, item in enumerate(config):
    with cols[i % 2]:
        d = get_data(item['name'], item['symbol'])
        p, v = d['p'], d['v']
        
        if item['symbol'] == "GC=F" and p > 0:
            p, v = [(x * fx / 31.1035) for x in [p, v]]

        diff, pct = p - v, ( (p-v)/v*100 if v>0 else 0 )
        color = "#30d158" if pct >= 0 else "#ff453a"

        # 💡 エラーの原因だった書き方を、最も安定した方法に修正
        if p > 1000:
            disp_p = f"{p:,.1f}"
        else:
            disp_p = f"{p:,.2f}"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{item['name']}</div>
            <div style="font-size: 10px; color: #636366; margin-bottom: 8px;">{ut}</div>
            <div class="price-val">{disp_p}</div>
            <div class="change-val" style="color: {color};">{diff:+,.1f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        if d['h']:
            fig = go.Figure(data=go.Scatter(y=d['h'], mode='lines', line=dict(color='#007aff', width=3)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=80, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"g_{i}")

time.sleep(60)
st.rerun()
