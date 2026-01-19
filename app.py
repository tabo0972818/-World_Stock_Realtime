import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Market Pro Fix", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; margin-bottom: 2px; }
    .update-time { font-size: 9px; color: #636366; margin-bottom: 5px; }
    .price-val { font-size: 24px; font-weight: bold; color: #ffffff; line-height: 1.1; }
    .change-val { font-size: 14px; font-weight: bold; margin-bottom: 8px; }
    .info-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .info-table td { border: 1px solid #3a3a3c; padding: 3px; font-size: 10px; color: #ffffff; }
    .info-label { background-color: #2c2c2e; font-weight: bold; width: 40%; text-align: left; }
    .info-value { text-align: right; font-weight: bold; background-color: #1c1c1e; }
    </style>
    """, unsafe_allow_html=True)

symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

def get_data():
    try:
        t = Ticker(symbols)
        prices = t.price
        # データが取れない時のために期間を少し長めに確保
        history = t.history(period="1d", interval="2m")
        return prices, history
    except:
        return None, None

prices_data, history_data = get_data()
fx_rate = prices_data['JPY=X'].get('regularMarketPrice', 150.0) if prices_data else 150.0
current_time = datetime.now().strftime("%H:%M:%S")

cols = st.columns(3)

if prices_data:
    for i, s in enumerate(symbols):
        with cols[i % 3]:
            p = prices_data.get(s)
            if isinstance(p, dict):
                curr = p.get('regularMarketPrice', 0)
                prev = p.get('regularMarketPreviousClose', 0)
                high = p.get('regularMarketDayHigh', curr)
                low = p.get('regularMarketDayLow', curr)
                
                # 💡 データが0やNoneの場合の補完対策
                if curr == 0 and prev != 0: curr = prev
                if high == 0: high = curr
                if low == 0: low = curr

                if s == "GC=F":
                    curr, prev, high, low = [(v * fx_rate / 31.1035) for v in [curr, prev, high, low]]

                diff = curr - prev
                pct = (diff / prev * 100) if prev != 0 else 0
                color = "#30d158" if pct >= 0 else "#ff453a"

                st.markdown(f'''
                    <div class="card-container">
                        <div class="stock-name">{flags[i]} {names[i]}</div>
                        <div class="update-time">{current_time} 更新</div>
                        <div class="price-val">{curr:,.2f}</div>
                        <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>
                ''', unsafe_allow_html=True)
                
                try:
                    df = history_data.loc[s]['close'].dropna()
                    fig = go.Figure(data=go.Scatter(y=df, mode='lines', line=dict(color='#007aff', width=2)))
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0), height=70,
                        xaxis_visible=False, yaxis_visible=False,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        # 💡 触っても反応しない（ズームやツールバー無効）設定
                        dragmode=False, hovermode=False
                    )
                    # 💡 config={'staticPlot': True} で完全固定化
                    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"f_{s}")
                except:
                    st.write("チャート読込中...")

                st.markdown(f'''
                        <table class="info-table">
                            <tr><td class="info-label">終値</td><td class="info-value">{prev:,.2f}</td></tr>
                            <tr><td class="info-label">高値</td><td class="info-value">{high:,.2f}</td></tr>
                            <tr><td class="info-label">安値</td><td class="info-value">{low:,.2f}</td></tr>
                        </table>
                    </div>
                ''', unsafe_allow_html=True)

time.sleep(30)
st.rerun()
