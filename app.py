import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
import plotly.graph_objects as go

# 💡 Web版でデザインを強制適用するための設定
st.set_page_config(page_title="Market Pro", layout="wide", initial_sidebar_state="collapsed")

# 💡 CSSを修正（!importantを多用してWeb版の白背景を強制的に上書き）
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white !important; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 10px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 8px; text-align: center;
    }
    .stock-name { font-size: 13px; font-weight: bold; color: #8e8e93; }
    .price-val { font-size: 24px; font-weight: bold; color: #ffffff; }
    .change-val { font-size: 15px; font-weight: bold; margin-bottom: 5px; }
    .info-table { width: 100%; border-collapse: collapse; background-color: #ffffff; color: #000000; }
    .info-table td { border: 1px solid #3a3a3c; padding: 2px; font-size: 10px; }
    </style>
    """, unsafe_allow_html=True)

symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

def get_data():
    try:
        t = Ticker(symbols)
        prices = t.price
        # 💡 チャート取得を安定させるため、期間を少し長めに設定
        history = t.history(period="5d", interval="15m")
        return prices, history
    except:
        return None, None

st.title("📊 市場監視ダッシュボード")

prices_data, history_data = get_data()
fx_rate = prices_data['JPY=X'].get('regularMarketPrice', 150.0) if prices_data else 150.0

cols = st.columns(3)

if prices_data and not history_data.empty:
    for i, s in enumerate(symbols):
        with cols[i % 3]:
            p = prices_data.get(s)
            if isinstance(p, dict):
                curr = p.get('regularMarketPrice', 0)
                prev = p.get('regularMarketPreviousClose', 1)
                
                # ゴールド計算
                if s == "GC=F":
                    curr, prev = [(v * fx_rate / 31.1035) for v in [curr, prev]]

                diff = curr - prev
                pct = (diff / prev) * 100
                color = "#30d158" if pct >= 0 else "#ff453a"

                st.markdown(f'''<div class="card-container">
                    <div class="stock-name">{flags[i]} {names[i]}</div>
                    <div class="price-val">{curr:,.2f}</div>
                    <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>''', unsafe_allow_html=True)
                
                # 💡 PlotlyのグラフをWeb版で確実に出すための書き方
                try:
                    df = history_data.loc[s]
                    fig = go.Figure(data=go.Scatter(y=df['close'], mode='lines', line=dict(color='#0a84ff', width=2)))
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0), height=60,
                        xaxis_visible=False, yaxis_visible=False,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"fig_{s}")
                except:
                    st.write("チャート読込中...")

                st.markdown(f'''
                    <table class="info-table">
                        <tr><td>終値</td><td style="text-align:right">{prev:,.2f}</td></tr>
                    </table></div>''', unsafe_allow_html=True)

# 💡 Web版の負荷を考え、更新を30秒に調整
time.sleep(30)
st.rerun()
