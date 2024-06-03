import os
import numpy as np
import datetime
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from ta.volatility import BollingerBands
from ta.trend import MACD

# 页面设置
st.set_page_config(layout="wide")

# 页面标题
html_temp = """
    <div style="background-color:#3872fb;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">金融資料視覺化呈現 (金融看板) </h1>
    <h2 style="color:white;text-align:center;">Financial Dashboard </h2>
    </div>
    """
stc.html(html_temp)

@st.cache
def load_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return df

# 用户输入
st.sidebar.subheader("选择股票和时间范围")
ticker = st.sidebar.text_input('输入股票代码', '2330.TW')
start_date = st.sidebar.date_input('开始日期', datetime.date(2022, 1, 1))
end_date = st.sidebar.date_input('结束日期', datetime.date(2022, 11, 18))

# 加载数据
df = load_data(ticker, start_date, end_date)

# 转换为datetime
df.reset_index(inplace=True)

# 选择K线时间长度
st.sidebar.subheader("K线设置")
cycle_duration = st.sidebar.number_input('K线时间长度（分钟）', value=1440)

# 选择技术指标参数
st.sidebar.subheader("技术指标设置")
long_ma_period = st.sidebar.slider('长MA周期', 0, 100, 10)
short_ma_period = st.sidebar.slider('短MA周期', 0, 100, 2)
long_rsi_period = st.sidebar.slider('长RSI周期', 0, 100, 14)
short_rsi_period = st.sidebar.slider('短RSI周期', 0, 100, 7)

# 计算技术指标
df['MA_long'] = df['Close'].rolling(window=long_ma_period).mean()
df['MA_short'] = df['Close'].rolling(window=short_ma_period).mean()

# RSI计算
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI_long'] = calculate_rsi(df, long_rsi_period)
df['RSI_short'] = calculate_rsi(df, short_rsi_period)
df['RSI_Middle'] = 50

# 布林带
indicator_bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
df['bb_bbm'] = indicator_bb.bollinger_mavg()
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()

# MACD
macd = MACD(close=df["Close"])
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()

# 绘图
st.subheader("K线图与技术指标")

fig = make_subplots(specs=[[{"secondary_y": True}]])

# K线图
fig.add_trace(go.Candlestick(x=df['Date'],
                             open=df['Open'],
                             high=df['High'],
                             low=df['Low'],
                             close=df['Close'],
                             name='K线'), secondary_y=True)

# 成交量
fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='成交量'), secondary_y=False)

# 长短MA
fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_long'], line=dict(color='blue', width=1), name='长MA'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_short'], line=dict(color='red', width=1), name='短MA'))

# 布林带
fig.add_trace(go.Scatter(x=df['Date'], y=df['bb_bbm'], line=dict(color='black', width=1), name='BBM'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['bb_bbh'], line=dict(color='green', width=1), name='BBH'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['bb_bbl'], line=dict(color='green', width=1), name='BBL'))

# 长短RSI
fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_long'], line=dict(color='purple', width=1), name='长RSI'), secondary_y=False)
fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI_short'], line=dict(color='orange', width=1), name='短RSI'), secondary_y=False)

# MACD
fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], line=dict(color='black', width=1), name='MACD'), secondary_y=True)
fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD_signal'], line=dict(color='red', width=1), name='MACD Signal'), secondary_y=True)

fig.update_layout(title='金融数据可视化',
                  yaxis_title='价格',
                  xaxis_title='日期',
                  yaxis2_title='技术指标')

st.plotly_chart(fig, use_container_width=True)
















