import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Perfect", layout="wide", initial_sidebar_state="collapsed")

# CSS（黒背景・固定デザイン）
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

symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "₿ BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", ""]

# 💡 各銘柄の状態を独立して管理（一つがコケても他を動かす）
if 'persistent_data' not in st.session_state:
    st.session_state.persistent_data = {s: {'price': 0.0, 'prev': 0.0, 'hist': []} for s in symbols}

def fetch_safe(symbol):
    try:
        t = Ticker(symbol)
        # 💡 価格情報
        p = t.price[symbol]
        curr = p.get('regularMarketPrice') or p.get('regularMarketPreviousClose') or 0.0
        prev = p.get('regularMarketPreviousClose') or curr
        
        # 💡 TOPIX先物などが0の場合の補完処理
        if curr == 0 and prev != 0: curr = prev
        if curr != 0: st.session_state.persistent_data[symbol]['price'] = curr
        if prev != 0: st.session_state.persistent_data[symbol]['prev'] = prev

        # 💡 履歴（グラフ用）
        try:
            h = t.history(period="3d", interval="30m")
            if not h.empty and symbol in h.index:
                hist_list = h.loc[symbol]['close'].dropna().tolist()
                if hist_list: st.session_state.persistent_data[symbol]['hist'] = hist_list
        except: pass
    except: pass
    return st.session_state.persistent_data[symbol]

# 画面表示
current_time = datetime.now().strftime("%H:%M:%S")
cols = st.columns(3)

# ドル円を真っ先に確保
fx = fetch_safe("JPY=X")
fx_rate = fx['price'] or 150.0

for i, s in enumerate(symbols):
    with cols[i % 3]:
        data = fetch_safe(s)
        curr, prev = data['price'], data['prev']
        
        # ゴールド計算
        if s == "GC=F" and curr != 0:
            curr, prev = [(v * fx_rate / 31.1035) for v in [curr, prev]]

        diff = curr - prev
        pct = (diff / prev * 100) if prev != 0 else 0
        color = "#30d158" if pct >= 0 else "#ff453a"

        st.markdown(f'''<div class="card-container">
            <div class="stock-name">{flags[i]} {names[i]}</div>
            <div class="update-time">{current_time} 更新</div>
            <div class="price-val">{curr:,.2f}</div>
            <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
        
        # 💡 グラフ表示（データがあれば表示、なければ「待機中」）
        if data['hist']:
            fig = go.Figure(data=go.Scatter(y=data['hist'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"fig_{s}")
        else:
            st.write("チャート読込中...")

        st.markdown(f'''<table class="info-table"><tr><td style="background-color:#2c2c2e; width:40%;">終値</td><td style="text-align:right">{prev:,.2f}</td></tr></table></div>''', unsafe_allow_html=True)

# 💡 自動更新を1分に設定（安定性重視）
time.sleep(10)
st.rerun()
