import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Max", layout="wide", initial_sidebar_state="collapsed")

# CSS（デザイン固定）
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
    .info-label { background-color: #2c2c2e; font-weight: bold; width: 40%; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

# 💡 成功データを保存する仕組み（セッション）
if 'data_store' not in st.session_state:
    st.session_state.data_store = {s: {'price': 0, 'prev': 0, 'high': 0, 'low': 0, 'hist': []} for s in symbols}

def update_all_data():
    try:
        t = Ticker(symbols)
        p = t.price
        # 💡 通信エラーを避けるため、期間を3日に絞り、インターバルを広げる
        h = t.history(period="3d", interval="30m")
        
        for s in symbols:
            if isinstance(p, dict) and s in p and isinstance(p[s], dict):
                info = p[s]
                curr = info.get('regularMarketPrice') or info.get('regularMarketPreviousClose') or st.session_state.data_store[s]['price']
                if curr != 0:
                    st.session_state.data_store[s]['price'] = curr
                    st.session_state.data_store[s]['prev'] = info.get('regularMarketPreviousClose') or st.session_state.data_store[s]['prev']
                    st.session_state.data_store[s]['high'] = info.get('regularMarketDayHigh') or curr
                    st.session_state.data_store[s]['low'] = info.get('regularMarketDayLow') or curr
            
            try:
                if not h.empty and s in h.index:
                    st.session_state.data_store[s]['hist'] = h.loc[s]['close'].dropna().tolist()
            except: pass
    except:
        pass

update_all_data()
fx_rate = st.session_state.data_store['JPY=X']['price'] or 150.0
current_time = datetime.now().strftime("%H:%M:%S")

cols = st.columns(3)
for i, s in enumerate(symbols):
    with cols[i % 3]:
        d = st.session_state.data_store[s]
        curr, prev = d['price'], d['prev']
        
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
        
        if d['hist']:
            fig = go.Figure(data=go.Scatter(y=d['hist'], mode='lines', line=dict(color='#007aff', width=2)))
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"f_{s}")
        else:
            st.write("データ待機中...")

        st.markdown(f'''<table class="info-table"><tr><td class="info-label">終値</td><td style="text-align:right">{prev:,.2f}</td></tr></table></div>''', unsafe_allow_html=True)

time.sleep(60)
st.rerun()
