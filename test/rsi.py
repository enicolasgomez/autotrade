from unittest import result
import yfinance as yf
#from pandas_datareader import data as pdr
import datetime as dt
import talib as ta 
import numpy as np 
import pandas as pd
import math
import matplotlib.pyplot as plt

#yf.pdr_override()

def computeRSI (data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)

    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi

def stochastic(data, k_window, d_window, window):
  # input to function is one column from df
  # containing closing price or whatever value we want to extract K and D from
  min_val  = data.rolling(window=window, center=False).min()
  max_val = data.rolling(window=window, center=False).max()
  stoch = ( (data - min_val) / (max_val - min_val) ) * 100
  K = stoch.rolling(window=k_window, center=False).mean() 
  D = K.rolling(window=d_window, center=False).mean() 
  return K, D

def to_hourly_data(df, hours):

  column_names = ["Date", "Open", "High", "Low", "close", "Volume"]
  result_df = pd.DataFrame(columns = column_names)

  current_index = 0
  current_low = 1000000000
  current_high = 0
  total_vol = 0
  open = 0
  date = 0

  for row in df.iterrows():
    date = row[0]
    row = row[1]
    if current_index < hours:
      if current_index == 0:
        open = row['Open']
      if row['Low'] < current_low:
        current_low = row['Low']
      if row['High'] > current_high:
        current_high = row['High']
      total_vol = total_vol + row['Volume']
      current_index = current_index + 1
    else:
      close = row['close']
      new_row = [date, open, current_high, current_low, close, total_vol]
      result_df = pd.concat([pd.DataFrame([new_row],columns=result_df.columns),result_df],ignore_index=True)
      open = 0
      current_index = 0
      current_low = 1000000000
      current_high = 0
      total_vol = 0
  return result_df

rsi_length = 14
# end_date = dt.datetime.today()
# start_date = end_date - dt.timedelta(days=950)
# stock = 'BTC-USD'
# #df = pdr.get_data_yahoo(stock, start_date, end_date)
# ticker = yf.Ticker(stock)
# df = ticker.history(interval="1H",start="2021-05-01",end="2022-05-18")

from Historic_Crypto import HistoricalData

#df = HistoricalData('BTC-USD',3600,'2015-01-01-00-00').retrieve_data()
#df.to_pickle("df.pkl")

df = pd.read_pickle("df.pkl")
#df = to_hourly_data(df, 4)

df['RSI'] = computeRSI(df['close'], rsi_length)
df['K'], df['D'] = stochastic(df['RSI'], 3, 3, rsi_length)

def plot_srsi(k, d):
  x_axis = range(0, len(k))

  plt.plot(x_axis, k, 'k', label='Line y')
  plt.plot(x_axis, d, 'd', label='Line z')

  plt.legend()
  plt.show()

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

def AngleBtw2Points(pointA, pointB):
  changeInX = pointB.x - pointA.x
  changeInY = pointB.y - pointA.y
  return math.degrees(math.atan2(changeInY,changeInX)) 

def CrossOver(pointA1, pointA2, pointB1):
  if pointA1.y > pointB1.y and pointA2.y < pointB1.y:
    return -1
  elif pointA1.y < pointB1.y and pointA2.y > pointB1.y:
    return 1
  else:
    return 0

df = df.reset_index()  # make sure indexes pair with number of rows
last_row = None
signal_row = None 
openPosition = None 
positions = []
profit_vector = []
total_profit = 0
signal_angle_enty = 0

#angle in which K crossed D 
signal_angle = 5
#angle in which K crossed D, given an open position. If lower than this then closed. (tendency change)
signal_angle_retire = 15
signal_bar_retire = 2
current_signal_bar = 0

#plot_srsi(df['K'], df['D'])
profit = 0
for index, row in df.iterrows(): 
  close = row['close']
  date = row['time']
  if index > rsi_length + 20 and last_row is not None:
    startK = Point(0, last_row['K']) #using 0 to 100 as SRSI is an oscillator (0, 100)
    startD = Point(0, last_row['D'])
    endK = Point(25, row['K'])
    endD = Point(25, row['D']) 
    angle = AngleBtw2Points(startK, endK)
    if not openPosition:
      crossOver = CrossOver(startK, endK, startD) #K crosses D
      if crossOver != 0:
        if abs(angle) > signal_angle and (crossOver * angle > 0): #checking if crossOver and angle have the same sign
          signal_angle_entry = angle
          if angle > 0:
            signal_row = row
            openPosition = Position(close, 'BUY', date)
            #openPosition.set_stop_loss(close * 0.95)
            #openPosition.set_take_profit(close * 1.01)
          else:
            signal_row = row
            openPosition = Position(close, 'SELL', date)
            #openPosition.set_stop_loss(close * 1.05)
            #openPosition.set_take_profit(close * 0.9)
    else:
      #openPosition.evaluate(close, date)
      #if openPosition.is_closed():
      openPosition.close(close, date)
      positions.append(openPosition)
      total_profit = total_profit + openPosition.profit
      profit_vector.append(total_profit)
      openPosition = None 
      signal_row = None 
      openPosition = None 

  last_row = row
plot_profit(profit_vector)
print()