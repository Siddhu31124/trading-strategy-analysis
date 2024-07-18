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
def calculate_rsi(data, window=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = abs(delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['rsi'] = calculate_rsi(df)
df=df.dropna()
df['pct_rsi']=df['rsi'].pct_change()
df['Daily_Returns'] = df['Close'].pct_change()
df['max']=df['Close'].cummax()
df['volume SMA']=df['Volume'].rolling(window=10).mean()
df['sma'] = df['price'].rolling(window=20).mean()
df['stdev']=df['price'].rolling(window=20).std()
df['upper'] = df['sma'] + 2 * df['stdev']
df['lower'] = df['sma'] - 2 * df['stdev']

df=df.dropna()
df['drawdown']=np.min((df['Close']-df['max'])/df['max'],0)
buy=[]
sell=[]
df['buy_signal']=0
df['sell_signal']=0
df['position']=0
selena=0
pos=False
imp=False
for index,row in df.iterrows() :
    if ((row['rsi'] < 40 and row['lower']>row['Close'] and row['pct_rsi']>0 ) or (row['gap_buy']==1))and row['Volume'] > row['volume SMA']  :
        if pos ==False:
            buy.append(index)
            pos=True
            df.loc[index,'buy_signal']=1
            selena=1
            if row['gap_buy']==1:
                imp=True
    elif (row['rsi'] > 60 and row['upper']<row['Close'] and row['pct_rsi']<0) or(0.92*row['prev_low']>row['Close'] and imp):
        if pos==True:
            sell.append(index)
            pos=False
            selena=0
            df.loc[index,'sell_signal']=1
            if imp:
                imp=False
    df.loc[index,'position']=selena 
    
plt.figure(figsize=(20,8))
plt.plot(df[['Close','sma','upper','lower']])
plt.legend(['Close','sma','upper','lower'])
plt.figure(figsize=(20,8))
plt.scatter(df.loc[buy].index,df.loc[buy,'Close'],marker='^',color='g')
plt.scatter(df.loc[sell].index,df.loc[sell,'Close'],marker='v',color='r')
plt.plot(df['Close'])
plt.legend(['buy','sell','Close'])
plt.figure(figsize=(20,8))
plt.plot(df['rsi'])
plt.axhline(y=70, color='r', linestyle='--')
plt.axhline(y=30, color='g', linestyle='--')
merged=pd.concat([df.loc[buy].price,df.loc[sell].price],axis=1)
merged.columns=['buys','sells']
merged=merged.sort_index()
profits=merged['sells'].shift(-1)-merged['buys']
temp=profits.notna()
profits_and_losses= profits[temp]
num_trades=len(profits_and_losses)
total_profits=profits_and_losses.sum()
max_profit_price=profits.max()
win_percent=profits.gt(0).sum()/num_trades
max_loss_price=np.min(profits.min(),0)
total_return =(total_profits/merged.iloc[0]['buys'])
anual_return=0
if 1+total_return>0:
    anual_return=(pow(1+total_return,1/8)-1)*100
sharpe_ratio = (anual_return-7.31)/(df['Daily_Returns'].std()* np.sqrt(252)) 
max_drawdown= df['drawdown'].min()
portfolio_value=merged.iloc[0]['buys']+ total_profits
print('the portfolio value is ',portfolio_value)
print('the total profit by this strtegy is',total_profits)
print('the absolute returns is',total_return*100)
print('the annualised returns are',anual_return)
print('the win percent is',win_percent*100)
print('the num of trades taken are',num_trades)
print('the maximum amount of profit made in one trade is',max_profit_price)
print('the maximum loss in one trade is ',max_loss_price)
print('the maximum drawdown is',max_drawdown)
print('the sharpe ratio is',sharpe_ratio)
plt.show()

