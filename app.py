import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

# 💡 ページ設定（コンソールの負担を最小限に）
st.set_page_config(page_title="Market Pro Fix", layout="wide", initial_sidebar_state="collapsed")

# 漆黒のデザイン
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 15px; 
        background-color: #1c1c1e; margin-bottom: 12px; text-align: center; min-height: 220px;
    }
    .stock-name { font-size: 14px; font-weight: bold; color: #8e8e93; margin-bottom: 5px; }
    .price-val { font-size: 32px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    .info-table { width: 100%; border-top: 1px solid #3a3a3c; margin-top: 10px; }
    .info-table td { padding: 5px; font-size: 12px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 💡 指定の8銘柄に絞り、止まりやすい銘柄は代替シンボルを使用
config = [
    {"name": "日経平均", "symbol": "^N225"},
    {"name": "日経先物", "symbol": "NIY=F"},
    {"name": "日経時間外", "symbol": "NIY=F"}, # 配信停止のNK225E=Fの代わり
    {"name": "TOPIX", "symbol": "1306.T"},
    {"name": "TOPIX先物", "symbol": "1306.T"}, # 配信停止のMTI=Fの代わり
    {"name": "ドル円", "symbol": "JPY=X"},
    {"name": "ゴールド(円/g)", "symbol": "GC=F"},
    {"name": "BTC(円)", "symbol": "BTC-JPY"}
]

if 'p_store' not in st.session_state:
    st.session_state.p_store = {c['name']: {'p': 0.0, 'v': 0.0, 'h': []} for c in config}

def fetch_yfinance(name, symbol):
    try:
        # 💡 yfinanceに切り替えて確実に取得
        ticker = yf.Ticker(symbol)
        data = ticker.fast_info
        
        curr = data['last_price']
        prev = data['previous_close']
        
        if curr > 0: st.session_state.p_store[name]['p'] = curr
        if prev > 0: st.session_state.p_store[name]['v'] = prev

        # 履歴
        h = ticker.history(period="3d", interval="30m")
        if not h.empty:
            vals = h['Close'].dropna().tolist()
            if vals: st.session_state.p_store[name]['h'] = vals
    except: pass
    return st.session_state.p_store[name]

# 描画開始
update_time = datetime.now().strftime("%H:%M:%S")
fx_rate = fetch_yfinance("ドル円", "JPY=X")['p'] or 150.0

cols = st.columns(2)

for i, item in enumerate(config):
    with cols[i % 2]:
        d = fetch_yfinance(item['name'], item['symbol'])
        p, v = d['p'], d['v']
        
        # ゴールド計算
        if item['symbol'] == "GC=F" and p > 0:
            p, v = [(x * fx_rate / 31.1035) for x in [p, v]]

        diff = p - v
        pct = (diff / v * 100) if v > 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{item['name']}</div>
            <div style="font-size: 10px; color: #636366; margin-bottom: 8px;">{update_time} 更新</div>
            <div class="price-val">{p:,.1f if p > 1000 else ,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.1f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        if d['h']:
            fig = go.Figure(data=go.Scatter(y=d['h'], mode='lines', line=dict(color='#007aff', width=3)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=80, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"k_{i}")

time.sleep(60)
st.rerun()
