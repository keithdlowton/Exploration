# %%

# %%
from urllib.request import urlopen

import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup
from plotly.subplots import make_subplots


# %%
def get_sp500_tickers():
    sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = urlopen(sp500_url)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    tickers = []
    for row in table.find_all("tr")[1:]:
        ticker = row.find_all("td")[0].text.strip()
        tickers.append(ticker)
    return tickers


# %%
# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# %%

# Fetch S&P 500 tickers
stable_sp500_tickers = get_sp500_tickers()
# %%

df = yf.download(symbol, period=select_period, interval="1d")
df = df.reset_index()

# Calculate MACD and Signal Line
df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
df["MACD"] = df["EMA12"] - df["EMA26"]
df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
# Calculate RSI
df["RSI"] = calculate_rsi(df)

# Set the title of the web-page
st.title("SBG Stock Analysis Portal")

# Setting up selection button for stocks
select_stock = st.sidebar.selectbox("Select a Stock", stable_sp500_tickers)

# Setting up selection button for period
select_period = st.sidebar.radio("Set period of analysis", options=["1mo", "3mo", "1y", "5y"])

# Create subplots with shared x-axis
fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    subplot_titles=(f"{symbol} Stock Price", "MACD", "RSI"),
    row_heights=[0.7, 0.1, 0.2],
)

# Add candlestick chart
fig.add_trace(
    go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candlestick"
    ),
    row=1,
    col=1,
)


fig.add_trace(
    go.Bar(
        x=df["Date"],
        y=df["Signal_Line"],
        marker=dict(color=df["Signal_Line"].apply(lambda x: "red" if x < 0 else "blue")),
        name="MACD",
    ),
    row=2,
    col=1,
)

fig.add_trace(go.Line(x=df["Date"], y=df["RSI"], marker=dict(color="magenta"), name="RSI"), row=3, col=1)

# Update layout for the plot
fig.update_layout(
    title=f"{symbol} Stock Trends", yaxis_title="Price", xaxis_title="Date", xaxis_rangeslider_visible=False
)

# Display the plot
st.plotly_chart(fig)

# %%
if __name__ == "__main__":
    ticker = input("Enter the stock ticker: ").upper()
    period = input("Enter the period (e.g., '1d', '1mo', '1y'): ").strip()

    stock_data = yf.download(ticker, period=period)

    mpf.plot(stock_data, type="candle", style="yahoo", title=f"Candlestick Chart for {ticker} ({period})")
