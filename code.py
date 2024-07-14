import pandas as pd 
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
ticker = 'ADANIENT.NS'
df = yf.download(ticker, start='2023-07-10', end='2024-07-10', interval='1d')
df['price']=df['Open'].shift(-1)
df['prev_high']=df['High'].shift(1)
df['prev_low']= df['Low'].shift(1)
df['prev_close']=df['Close'].shift(1)
df['gap_buy'] = np.where(
    (df['Open'] > df['prev_high']) 
| (((df['High'] - df['Close']) < 0.3 * (df['High'] - df['Low'])) & 
((df['Open'] - df['Low']) < 0.3 * (df['High'] - df['Low']))),1,0)  
df['gap_sell']=np.where((df['Open']<df['prev_low'])
| (((df['High'] - df['Open']) < 0.3 * (df['High'] - df['Low'])) & 
((df['Close'] - df['Low']) < 0.3 * (df['High'] - df['Low']))),1,0)
