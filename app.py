import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

# 💡 コンソール負荷軽減のため、不要なツールバーを無効化
st.set_page_config(page_title="Market Fix", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center; min-height: 230px;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; }
    .price-val { font-size: 24px; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .change-val { font-size: 14px; font-weight: bold; }
    .info-table { width: 100%; margin-top: 10px; border-top: 1px solid #3a3a3c; }
    .info-table td { padding: 5px; font-size: 11px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 💡 銘柄リスト（シンボルをより確実なものへ微調整）
symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]

if 'cache' not in st.session_state:
    st.session_state.cache = {s: {'p': 0.0, 'v': 0.0, 'h': []} for s in symbols}

def fetch_fast(s):
    try:
        # 💡 非同期（並列）をやめて1つずつ取得し、コンソールのパニックを防ぐ
        t = Ticker(s, asynchronous=False, retry=2, timeout=5)
        p = t.price[s]
        
        # データが空の場合の予備取得
        curr = p.get('regularMarketPrice') or p.get('regularMarketPreviousClose') or 0.0
        prev = p.get('regularMarketPreviousClose') or curr
        
        if curr > 0: st.session_state.cache[s]['p'] = curr
        if prev > 0: st.session_state.cache[s]['v'] = prev

        # 💡 グラフ取得（ここが重いので、失敗したら即諦める設定）
        try:
            h = t.history(period="2d", interval="30m")
            if not h.empty:
                vals = h.iloc[:, 0].dropna().tolist()
                if vals: st.session_state.cache[s]['h'] = vals
        except: pass
    except: pass
    return st.session_state.cache[s]

# 描画
cols = st.columns(3)
fx_rate = fetch_fast("JPY=X")['p'] or 150.0

for i, s in enumerate(symbols):
    with cols[i % 3]:
        d = fetch_fast(s)
        p, v = d['p'], d['v']
        
        if s == "GC=F" and p > 0:
            p, v = [(x * fx_rate / 31.1035) for x in [p, v]]

        diff = p - v
        pct = (diff / v * 100) if v > 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{names[i]}</div>
            <div class="price-val">{p:,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        # 💡 グラフのツールバーを完全に消してコンソール警告を抑制
        if d['h']:
            fig = go.Figure(data=go.Scatter(y=d['h'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=60, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"c_{s}")
        
        st.markdown(f'''<table class="info-table"><tr><td>前日比</td><td style="text-align:right">{v:,.2f}</td></tr></table></div>''', unsafe_allow_html=True)

time.sleep(60)
st.rerun()
