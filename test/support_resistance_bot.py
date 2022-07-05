import pandas as pd
import numpy as np
import yfinance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [12, 7]
plt.rc('font', size=14) 

#name = 'ETH-USD'
#ticker = yfinance.Ticker(name)
#df = ticker.history(interval="1d",start="2021-05-01",end="2022-07-01")

#df.to_pickle("df.pkl")

df = pd.read_pickle("df.pkl")

df['Date'] = pd.to_datetime(df.index)
df['Date'] = df['Date'].apply(mpl_dates.date2num)

df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]

def plot_all(df, levels):
  fig, ax = plt.subplots()

  candlestick_ohlc(ax,df.values,width=0.6, \
                   colorup='green', colordown='red', alpha=0.8)

  date_format = mpl_dates.DateFormatter('%d %b %Y')
  ax.xaxis.set_major_formatter(date_format)
  fig.autofmt_xdate()

  fig.tight_layout()

  for level in levels:
    plt.hlines(level[1],xmin=df['Date'][level[0]],\
               xmax=max(df['Date']),colors='blue')


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
  closeDate = None
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
  def evaluate(self, price, date):
    if self.type == 'BUY':
      if price < self.stop_loss:
        self.close(self.stop_loss, date)
      if price > self.take_profit:
        self.close(self.take_profit, date)
    elif self.type == 'SELL':
      if price > self.stop_loss:
        self.close(self.stop_loss, date)
      if price < self.take_profit:
        self.close(self.take_profit, date)
  def is_closed(self):
    return self.close_price != 0 

#df.to_pickle("a_file.pkl")

#df = pd.read_pickle("a_file.pkl")

def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] \
  and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

  return support

def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] \
  and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2] 

  return resistance

def get_levels(df):
  levels = []
  for i in range(2,df.shape[0]-2):
    if isSupport(df,i):
      levels.append((i,df['Low'][i]))
    elif isResistance(df,i):
      levels.append((i,df['High'][i]))

  s =  np.mean(df['High'] - df['Low'])

  def isFarFromLevel(l):
    return np.sum([abs(l-x) < s  for x in levels]) == 0

  levels = []
  for i in range(2,df.shape[0]-2):
    if isSupport(df,i):
      l = df['Low'][i]

      if isFarFromLevel(l):
        levels.append((i,l))

    elif isResistance(df,i):
      l = df['High'][i]

      if isFarFromLevel(l):
        levels.append((i,l))
  return levels

positions = []
openPosition = None
total_profit = 0
profit_vector = []
prev_close = 0

for i in range(1, len(df)-30):
  #get date range
  start = df.index[i]
  end = df.index[i+30]

  #slice dataframe
  window = df.loc[start:end]
  levels = get_levels(window)
  last_close = window['Close'][len(window)-1]
  last_date =  window['Date'][len(window)-1]

  if openPosition:
    openPosition.evaluate(last_close, last_date)
    if openPosition.is_closed():
      positions.append(openPosition)
      total_profit = total_profit + openPosition.profit
      print(openPosition.profit)
      profit_vector.append(total_profit)
        
  else:
    #get last close
    if levels:
      resistance = levels[len(levels)-1][1]
      support = levels[len(levels)-2][1]

      mid = abs(support + resistance) / 2

      if last_close > support and prev_close < support:
        openPosition = Position(last_close, 'SELL', last_date)
      elif last_close < resistance and prev_close > resistance:
        openPosition = Position(last_close, 'BUY', last_date)

      if openPosition:
        openPosition.set_take_profit(mid)
        plot_all(window, levels)

    prev_close = last_close

plot_profit(profit_vector)
