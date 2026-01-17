import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px

st.set_page_config(page_title="World Stock Realtime", layout="wide")

# デザイン設定
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .card-container {
        border: 1px solid #3a3a3c; border-radius: 12px; padding: 10px; 
        background-color: #1c1c1e; margin-bottom: 20px; text-align: center;
    }
    .stock-name { font-size: 16px; font-weight: bold; color: #8e8e93; }
    .price-val { font-size: 30px; font-weight: bold; margin: 2px 0; }
    .change-val { font-size: 18px; font-weight: bold; }
    
    div.stButton > button {
        width: 100%;
        background-color: #007aff !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        height: 3em !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

stocks = [
    ("日経平均", "^N225", "🇯🇵"), ("ダウ平均", "^DJI", "🇺🇸"), ("ドル円", "JPY=X", "🇯🇵🇺🇸"),
    ("ナスダック", "^IXIC", "🇺🇸"), ("S&P500", "^GSPC", "🇺🇸"), ("BTC(円)", "BTC-JPY", "₿"),
    ("半導体SOX", "^SOX", "🇺🇸"), ("ゴールド", "GC=F", "🟡"), ("TOPIX", "1306.T", "🇯🇵")
]

def get_market_data(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=2m&range=1d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        result = res['chart']['result'][0]
        prices = result['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=['Price']).dropna()
        meta = result['meta']
        return {"df": df, "curr": meta['regularMarketPrice'], "prev": meta['previousClose']}
    except: return None

st.title("📈 世界の株価 Realtime")

if st.button("🔄 データを今すぐ更新"):
    st.rerun()

st.write("")

cols = st.columns(3)

for i, (name, ticker, flag) in enumerate(stocks):
    data = get_market_data(ticker)
    with cols[i % 3]:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        if data:
            pct = ((data['curr'] - data['prev']) / data['prev']) * 100
            color = "#30d158" if pct >= 0 else "#ff453a"
            
            st.markdown(f'<div class="stock-name">{flag} {name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-val">{data["curr"]:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="change-val" style="color: {color};">{pct:+.2f}%</div>', unsafe_allow_html=True)
            
            fig = px.line(data['df'], y='Price')
            
            # 💡【解決策】グラフに触っても反応しないようにする設定
            fig.update_layout(
                margin=dict(l=0, r=0, t=5, b=5),
                height=150,
                xaxis_visible=False,
                yaxis_visible=False,
                yaxis=dict(fixedrange=True, autorange=True), # ズーム不可
                xaxis=dict(fixedrange=True),                # ズーム不可
                hovermode=False,                             # ホバー時の数値を非表示
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                dragmode=False                               # ドラッグ操作を無効化
            )
            fig.update_traces(
                line_color='#1f77b4', 
                line_width=3,
                hoverinfo='none'                             # 個別のデータ点反応も消す
            )
            
            # configで右上のツールバーも非表示にする
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
            
        else:
            st.markdown(f'<div class="stock-name">{flag} {name}</div>', unsafe_allow_html=True)
            st.error("データ取得エラー")
        st.markdown('</div>', unsafe_allow_html=True)

time.sleep(10)
st.rerun()
