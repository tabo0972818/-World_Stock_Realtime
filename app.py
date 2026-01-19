import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

# 💡 コンソール負荷軽減のため設定
st.set_page_config(page_title="Market Pro Realtime", layout="wide", initial_sidebar_state="collapsed")

# 背景・カードデザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 12px; 
        background-color: #1c1c1e; margin-bottom: 10px; text-align: center; min-height: 240px;
    }
    .stock-name { font-size: 14px; font-weight: bold; color: #8e8e93; margin-bottom: 5px; }
    .price-val { font-size: 28px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    .info-table { width: 100%; border-top: 1px solid #3a3a3c; margin-top: 10px; }
    .info-table td { padding: 5px; font-size: 11px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 💡 【重要】配信が止まっている銘柄を、現在動いている代替銘柄に差し替えました
# 日経時間外（NK225E=F）→ NIY=F（CME日経先物：ほぼ24時間稼働）
# TOPIX先物（MTI=F）→ 1306.T（TOPIX ETF：現物データ）
symbols = ["^N225", "NIY=F", "NIY=F", "1306.T", "1306.T", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]

if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {s: {'p': 0.0, 'v': 0.0, 'h': []} for s in symbols}

def fetch_market_data(s):
    try:
        # 💡 コンソール警告を減らすため1つずつ取得
        t = Ticker(s, asynchronous=False)
        p_info = t.price[s]
        
        # 正常な価格が出るまで候補を探す
        curr = p_info.get('regularMarketPrice') or p_info.get('preMarketPrice') or p_info.get('regularMarketPreviousClose') or 0.0
        prev = p_info.get('regularMarketPreviousClose') or curr
        
        if curr > 0: st.session_state.data_cache[s]['p'] = curr
        if prev > 0: st.session_state.data_cache[s]['v'] = prev

        # 履歴取得
        try:
            h = t.history(period="3d", interval="30m")
            if not h.empty:
                h_list = h.iloc[:, 0].dropna().tolist()
                if h_list: st.session_state.data_cache[s]['h'] = h_list
        except: pass
    except: pass
    return st.session_state.data_cache[s]

# メイン描画
update_time = datetime.now().strftime("%H:%M:%S")
cols = st.columns(3)

# ドル円確保
fx_data = fetch_market_data("JPY=X")
current_fx = fx_data['p'] or 150.0

for i, s in enumerate(symbols):
    with cols[i % 3]:
        data = fetch_market_data(s)
        p, v = data['p'], data['v']
        
        # ゴールド円換算
        if s == "GC=F" and p > 0:
            p, v = [(val * current_fx / 31.1035) for val in [p, v]]

        diff = p - v
        pct = (diff / v * 100) if v > 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{names[i]}</div>
            <div style="font-size: 10px; color: #636366; margin-bottom: 8px;">{update_time} 更新</div>
            <div class="price-val">{p:,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        # チャート表示（コンソール警告抑制のため staticPlot 使用）
        if data['h']:
            fig = go.Figure(data=go.Scatter(y=data['h'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True}, key=f"chart_{i}")

        st.markdown(f'''<table class="info-table"><tr><td>前日終値</td><td style="text-align:right">{v:,.2f}</td></tr></table></div>''', unsafe_allow_html=True)

# 10s更新
time.sleep(10)
st.rerun()

