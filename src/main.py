import operator
from Historic_Crypto import HistoricalData
import pandas as pd
import numpy as np
import yfinance
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from AutoTrader.TradeBot import TradeBot
from itertools import accumulate

plt.rcParams['figure.figsize'] = [12, 7]
plt.rc('font', size=14) 

def plot_all(df, levels):
  fig, ax = plt.subplots()

  candlestick_ohlc(ax,df.values,width=0.6, \
                   colorup='green', colordown='red', alpha=0.8)

  date_format = mpl_dates.timeFormatter('%d %b %Y')
  ax.xaxis.set_major_formatter(date_format)
  fig.autofmt_xdate()

  fig.tight_layout()

  for level in levels:
    plt.hlines(level[1],xmin=df['time'][level[0]],\
               xmax=max(df['time']),colors='blue')


def plot_profit(p):
  x_axis = range(0, len(p))

  label = 'Profit - Max: {}'.format(str(p[-1]))
  plt.plot(x_axis, p, 'k', label=label )
  plt.legend()
  plt.show()

def retrieveData(symbol):
    #df = HistoricalData(symbol, 900,'2016-01-01-00-00', '2019-01-01-00-00').retrieve_data()
    #df.to_pickle("df-btcusd-2016-2019.pkl")

    df = pd.read_pickle("../df-btcusd.pkl")
    
    df['time'] = pd.to_datetime(df.index)
    df['time'] = df['time'].apply(mpl_dates.date2num)

    df = df.loc[:,['time', 'open', 'high', 'low', 'close']]
    
    return df

stock = 'BTC-USD'

df = retrieveData(stock)

bot = TradeBot()

l = len(df)
next_report = 0

for i in range(0, l):
  
  percProgress = i * 1.0 / l

  if percProgress >= next_report:
    print(f'Progress {round(percProgress * 100, 5)}')
    next_report = percProgress + 0.05

  bot.process_new_candle(df['time'].iloc[i], df['open'].iloc[i], df['close'].iloc[i], df['high'].iloc[i], df['low'].iloc[i])

profit_vector = list(accumulate([1 + p.profitAsPerc for p in bot.closed_positions], operator.mul))
plot_profit(profit_vector)
