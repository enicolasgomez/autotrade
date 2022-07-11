import pandas as pd
import numpy as np
import yfinance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [12, 7]
plt.rc('font', size=14) 

# name = 'ETH-USD'
# ticker = yfinance.Ticker(name)
# df = ticker.history(interval="1h",start="2021-05-01",end="2022-07-01")

# df.to_pickle("df.pkl")

#end_date = dt.datetime.today()
#start_date = end_date - dt.timedelta(days=950)

stock = 'BTC-USD'
from Historic_Crypto import HistoricalData

#df = HistoricalData(stock,900,'2016-01-01-00-00', '2019-01-01-00-00').retrieve_data()
#df.to_pickle("df-btcusd-2016-2019.pkl")

df = pd.read_pickle("df-btcusd.pkl")

df['time'] = pd.to_datetime(df.index)
df['time'] = df['time'].apply(mpl_dates.date2num)

df = df.loc[:,['time', 'open', 'high', 'low', 'close']]

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

  label = 'Profit - Max: {}'.format(str(p[len(p)-1]))
  plt.plot(x_axis, p, 'k', label=label )
  plt.legend()
  plt.show()

class Point:
  x = 0
  y = 0
  def __init__(self, x, y):
    self.x = x 
    self.y = y

class Position:
  open = 0
  close_price = 0
  profit = 0
  type = 0
  date = None
  closetime = None
  stop_loss = 0
  take_profit = 0
  def __init__(self, open, type, date):
    self.open = open 
    self.type = type
    self.date = date
  def close(self, price, date):
    self.close_price = price
    self.date = date
    self.calculate_profit(price)
  def calculate_profit(self, close):
    if self.type == 'BUY':
      self.profit = close - self.open
    else:
      self.profit = self.open - close
  def set_stop_loss(self, price):
    self.stop_loss = price
  def set_take_profit(self, price):
    self.take_profit = price
  def evaluate(self, high, low, date):
    if self.type == 'BUY':
      if low < self.stop_loss and self.stop_loss > 0:
        self.close(self.stop_loss, date)
      elif high > self.take_profit:
        self.close(self.take_profit, date)
    elif self.type == 'SELL':
      if high > self.stop_loss and self.stop_loss > 0:
        self.close(self.stop_loss, date)
      elif low < self.take_profit:
        self.close(self.take_profit, date)

  def is_closed(self):
    return self.close_price != 0 

#df.to_pickle("a_file.pkl")

#df = pd.read_pickle("a_file.pkl")

def isSupport(df,i):
  support = df['low'][i] < df['low'][i-1]  and df['low'][i] < df['low'][i+1] \
  and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]

  return support

def isResistance(df,i):
  resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] \
  and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2] 

  return resistance

def get_levels(df):
  levels = []
  for i in range(2,df.shape[0]-2):
    if isSupport(df,i):
      levels.append((i,df['low'][i]))
    elif isResistance(df,i):
      levels.append((i,df['high'][i]))

  s =  np.mean(df['high'] - df['low'])

  def isFarFromLevel(l):
    return np.sum([abs(l-x) < s  for x in levels]) == 0

  levels = []
  for i in range(2,df.shape[0]-2):
    if isSupport(df,i):
      l = df['low'][i]

      if isFarFromLevel(l):
        levels.append((i,l))

    elif isResistance(df,i):
      l = df['high'][i]

      if isFarFromLevel(l):
        levels.append((i,l))
  return levels

positions = []
openPosition = None
total_profit = 0
profit_vector = []
prev_close = -1

for i in range(1, len(df)-30):
  #get date range
  start = df.index[i]
  end = df.index[i+30]

  #slice dataframe
  window = df.loc[start:end]
  levels = get_levels(window)
  last_close = window['close'][len(window)-1]
  last_high = window['high'][len(window)-1]
  last_low = window['low'][len(window)-1]
  last_date =  window['time'][len(window)-1]

  non_profit_level = 0

  if levels:
    resistance = levels[len(levels)-2][1]
    support = levels[len(levels)-1][1]

    mid = abs(support + resistance) / 2

    if openPosition:
      openPosition.evaluate(last_high, last_low, last_date)
      if openPosition.is_closed():
        positions.append(openPosition)
        total_profit = total_profit + openPosition.profit
        profit_vector.append(total_profit)
        if openPosition.profit < 0:
          if non_profit_level == 0:
            non_profit_level = 1
            #reversal
            if openPosition.type == 'SELL':
              openPosition = Position(last_close, 'BUY', last_date)
              openPosition.set_take_profit(last_close * 1.02)
              openPosition.set_stop_loss(support)
            else:
              openPosition = Position(last_close, 'SELL', last_date)
              openPosition.set_take_profit(last_close * 0.98)
              openPosition.set_stop_loss(resistance)
          else:
            openPosition = None
        else:
          openPosition = None
          non_profit_level = 0
          
    else:
      #get last close

      if last_close < support and prev_close > support:
        openPosition = Position(last_close, 'BUY', last_date)
        openPosition.set_take_profit(last_close * 1.02)
        openPosition.set_stop_loss(last_close * 0.99)
      elif last_close > resistance and prev_close < resistance:
        openPosition = Position(last_close, 'SELL', last_date)
        openPosition.set_take_profit(last_close * 0.98)
        openPosition.set_stop_loss(last_close * 1.01)

    prev_close = last_close

plot_profit(profit_vector)
