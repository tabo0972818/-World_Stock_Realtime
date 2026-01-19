import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Perfect", layout="wide", initial_sidebar_state="collapsed")

# 背景黒・デザイン固定
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center; min-height: 280px;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; margin-bottom: 2px; }
    .update-time { font-size: 9px; color: #636366; margin-bottom: 5px; }
    .price-val { font-size: 24px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 14px; font-weight: bold; margin-bottom: 8px; }
    .info-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .info-table td { border: 1px solid #3a3a3c; padding: 3px; font-size: 10px; color: #ffffff; }
    .info-label { background-color: #2c2c2e; font-weight: bold; width: 40%; text-align: left; }
    .info-value { text-align: right; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

# 💡 前回の成功データを保持するためのセッション状態
if 'last_prices' not in st.session_state:
    st.session_state.last_prices = {}
if 'last_history' not in st.session_state:
    st.session_state.last_history = pd.DataFrame()

def fetch_data():
    try:
        t = Ticker(symbols)
        # 💡 通信エラーを避けるため、取得間隔を2分に設定
        h = t.history(period="3d", interval="15m")
        p = t.price
        if p and len(p) > 0:
            st.session_state.last_prices = p
            st.session_state.last_history = h
        return p, h
    except:
        return st.session_state.last_prices, st.session_state.last_history

prices_data, history_data = fetch_data()

# ドル円レートの安全な確保
fx_rate = 150.0
if isinstance(prices_data, dict) and 'JPY=X' in prices_data:
    fx_rate = prices_data['JPY=X'].get('regularMarketPrice') or 150.0

current_time = datetime.now().strftime("%H:%M:%S")
cols = st.columns(3)

for i, s in enumerate(symbols):
    with cols[i % 3]:
        st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="stock-name">{flags[i]} {names[i]}</div>', unsafe_allow_html=True)
        
        # 💡 データがある場合のみ描画
        if prices_data and s in prices_data and isinstance(prices_data[s], dict):
            p = prices_data[s]
            curr = p.get('regularMarketPrice') or p.get('regularMarketPreviousClose') or 0
            prev = p.get('regularMarketPreviousClose') or curr
            
            if s == "GC=F":
                curr, prev = [(v * fx_rate / 31.1035) for v in [curr, prev]]

            diff = curr - prev
            pct = (diff / prev * 100) if prev != 0 else 0
            color = "#30d158" if pct >= 0 else "#ff453a"

            st.markdown(f'<div class="update-time">{current_time} 更新</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-val">{curr:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>', unsafe_allow_html=True)
            
            # グラフ（固定設定）
            try:
                if not history_data.empty and s in history_data.index:
                    df = history_data.loc[s]['close'].dropna()
                    if not df.empty:
                        fig = go.Figure(data=go.Scatter(y=df, mode='lines', line=dict(color='#007aff', width=2)))
                        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=70, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
                        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"f_{s}")
            except: pass

            st.markdown(f'''
                <table class="info-table">
                    <tr><td class="info-label">終値</td><td class="info-value">{prev:,.2f}</td></tr>
                </table>''', unsafe_allow_html=True)
        else:
            # 💡 データが取れていない時のための仮表示
            st.markdown('<div style="height:150px; padding-top:50px; color:#636366;">データ再読み込み中...</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

# 💡 自動更新を1分に設定（API制限を避けるため）
time.sleep(60)
st.rerun()
