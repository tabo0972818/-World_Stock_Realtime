import streamlit as st
import pandas as pd
from yahooquery import Ticker
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Market Pro", layout="wide")

# (デザインCSSは省略...前回と同じものを使用してください)

# 取得したいシンボルをリスト化
symbols = ["^N225", "NIY=F", "NK225E=F", "1306.T", "MTI=F", "JPY=X", "^DJI", "^IXIC", "^SOX", "GC=F", "^GSPC", "BTC-JPY"]
names = ["日経平均", "日経先物", "日経時間外", "TOPIX", "TOPIX先物", "ドル円", "ダウ平均", "ナスダック", "半導体指数", "ゴールド(円/g)", "S&P500", "BTC(円)"]
flags = ["🇯🇵", "🇯🇵🚀", "🇯🇵⏰", "🇯🇵", "🇯🇵🚀", "🇯🇵🇺🇸", "🇺🇸", "🇺🇸", "🇺🇸🚀", "🟡", "🇺🇸", "₿"]

def get_all_data():
    try:
        t = Ticker(symbols)
        # 12銘柄の現在値を一括取得（爆速）
        prices = t.price
        # 12銘柄のチャートデータを一括取得
        history = t.history(period="1d", interval="2m")
        return prices, history
    except:
        return None, None

st.title("株価確認アプリ")

prices_data, history_data = get_all_data()
fx_rate = prices_data['JPY=X'].get('regularMarketPrice', 150.0) if prices_data else 150.0

cols = st.columns(3)

if prices_data:
    for i, s in enumerate(symbols):
        with cols[i % 3]:
            p = prices_data.get(s)
            if isinstance(p, dict):
                curr = p.get('regularMarketPrice', 0)
                prev = p.get('regularMarketPreviousClose', 1)
                high = p.get('regularMarketDayHigh', 0)
                low = p.get('regularMarketDayLow', 0)
                
                # ゴールド計算
                if s == "GC=F":
                    curr, prev, high, low = [(v * fx_rate / 31.1035) for v in [curr, prev, high, low]]

                diff = curr - prev
                pct = (diff / prev) * 100
                color = "#30d158" if pct >= 0 else "#ff453a"

                st.markdown(f'''
                    <div class="card-container">
                        <div class="stock-name">{flags[i]} {names[i]}</div>
                        <div class="price-val">{curr:,.2f}</div>
                        <div class="change-val" style="color: {color};">{diff:+,.2f} ({pct:+.2f}%)</div>
                ''', unsafe_allow_html=True)
                
                # チャート表示
                try:
                    df = history_data.loc[s]['close']
                    fig = px.line(y=df)
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=60, xaxis_visible=False, yaxis_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    fig.update_traces(line_color='#0a84ff', line_width=2)
                    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"fig_{s}")
                except: pass

                st.markdown(f'''
                        <table class="info-table">
                            <tr><td class="info-label">終値</td><td class="info-value">{prev:,.2f}</td></tr>
                            <tr><td class="info-label">高値</td><td class="info-value">{high:,.2f}</td></tr>
                            <tr><td class="info-label">安値</td><td class="info-value">{low:,.2f}</td></tr>
                        </table>
                    </div>
                ''', unsafe_allow_html=True)
else:
    st.error("データ取得エラー。API制限の可能性があります。")

time.sleep(20) # 20秒間隔が最速・安全のバランス
st.rerun()
