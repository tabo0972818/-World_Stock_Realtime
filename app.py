import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

# 💡 ページ設定
st.set_page_config(page_title="REALTIME MARKET BOARD", layout="wide", initial_sidebar_state="collapsed")

# 漆黒のデザイン
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    /* 💡 題名のスタイル */
    .main-title {
        font-size: 36px; font-weight: 800; color: #ffffff; text-align: center;
        margin-bottom: 20px; letter-spacing: 2px; border-bottom: 2px solid #007aff;
        padding-bottom: 10px; font-family: 'Arial Black', sans-serif;
    }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 15px; 
        background-color: #1c1c1e; margin-bottom: 12px; text-align: center; min-height: 200px;
    }
    .stock-name { font-size: 14px; font-weight: bold; color: #8e8e93; margin-bottom: 5px; }
    .price-val { font-size: 30px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    div.stButton > button {
        width: 100%; border-radius: 20px; background-color: #007aff; color: white; border: none; font-weight: bold; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 💡 画面に題名を表示
st.markdown('<div class="main-title">REALTIME MARKET BOARD</div>', unsafe_allow_html=True)

# 更新ボタン
if st.button('🔄 今すぐ最新データに更新'):
    st.rerun()

# 指定の12銘柄
config = [
    {"name": "日経平均", "symbol": "^N225"},
    {"name": "日経先物ラージ", "symbol": "NIY=F"},
    {"name": "日経時間外", "symbol": "NIY=F"},
    {"name": "TOPIX", "symbol": "1306.T"},
    {"name": "TOPIX先物", "symbol": "1306.T"},
    {"name": "ダウ平均", "symbol": "^DJI"},
    {"name": "ドル円 USD/JPY", "symbol": "JPY=X"},
    {"name": "ナスダック", "symbol": "^IXIC"},
    {"name": "半導体指数", "symbol": "^SOX"},
    {"name": "S&P500", "symbol": "^GSPC"},
    {"name": "ビットコイン国内", "symbol": "BTC-JPY"},
    {"name": "ゴールド円グラム", "symbol": "GC=F"}
]

if 'cache' not in st.session_state:
    st.session_state.cache = {c['name']: {'p': 0.0, 'v': 0.0, 'h': []} for c in config}

def get_data(name, symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        curr, prev = info['last_price'], info['previous_close']
        if curr > 0: st.session_state.cache[name]['p'] = curr
        if prev > 0: st.session_state.cache[name]['v'] = prev
        try:
            h = t.history(period="3d", interval="30m")
            if not h.empty: st.session_state.cache[name]['h'] = h['Close'].dropna().tolist()
        except: pass
    except: pass
    return st.session_state.cache[name]

ut = datetime.now().strftime("%H:%M:%S")
fx_rate = get_data("ドル円 USD/JPY", "JPY=X")['p'] or 150.0
cols = st.columns(3)

for i, item in enumerate(config):
    with cols[i % 3]:
        d = get_data(item['name'], item['symbol'])
        p, v = d['p'], d['v']
        if item['symbol'] == "GC=F" and p > 0: p, v = [(x * fx_rate / 31.1035) for x in [p, v]]
        diff, pct = p - v, ( (p-v)/v*100 if v>0 else 0 )
        color = "#30d158" if pct >= 0 else "#ff453a"
        disp_p = f"{p:,.1f}" if p > 1000 else f"{p:,.2f}"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{item['name']}</div>
            <div style="font-size: 10px; color: #636366; margin-bottom: 8px;">{ut} 更新</div>
            <div class="price-val">{disp_p}</div>
            <div class="change-val" style="color: {color};">{diff:+,.1f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        if d['h']:
            fig = go.Figure(data=go.Scatter(y=d['h'], mode='lines', line=dict(color='#007aff', width=3)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"k_{i}")

time.sleep(1)
st.rerun()
