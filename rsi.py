import yfinance as yf
from pandas_datareader import data as pdr
import datetime as dt
import talib as ta 
import numpy as np 
import math
import matplotlib.pyplot as plt

yf.pdr_override()

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

rsi_length = 14
end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=350)
stock = 'BTC-USD'
df = pdr.get_data_yahoo(stock, start_date, end_date)

df['RSI'] = computeRSI(df['Adj Close'], rsi_length)
df['K'], df['D'] = stochastic(df['RSI'], 3, 3, rsi_length)

def plot_srsi(k, d):
  x_axis = range(0, len(k))

  plt.plot(x_axis, k, 'k', label='Line y')
  plt.plot(x_axis, d, 'd', label='Line z')

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
  close = 0
  profit = 0
  type = 0
  def __init__(self, open, type):
    self.open = open 
    self.type = type
  def close(self, close):
    self.close = close
    self.calculate_profit(close)
  def calculate_profit(self, close):
    if type == 'BUY':
      profit = close - self.open
    else:
      profit = self.open - close 
def AngleBtw2Points(pointA, pointB):
  changeInX = pointB.x - pointA.x
  changeInY = pointB.y - pointA.y
  return math.degrees(math.atan2(changeInY,changeInX)) 

def CrossOver(pointA1, pointB1, pointA2, pointB2):
  if pointA1.y > pointB1.y and pointA2.y < pointB2.y:
    return -1
  elif pointA1.y < pointB1.y and pointA2.y > pointB2.y:
    return 1
  else:
    return 0

df = df.reset_index()  # make sure indexes pair with number of rows
last_row = None
signal_row = None 
openPosition = None 
positions = []

signal_angle = 45
signal_angle_retire = 10 

for index, row in df.iterrows():
  last_row = row 
  if index > rsi_length + 15:
    startK = Point(index-1, row['K'])
    startD = Point(index-1, row['D'])
    endK = Point(index, row['K'])
    endD = Point(index, row['D'])
    angle = AngleBtw2Points(startK, endK, startD, endD)
    if not openPosition:
      crossOver = CrossOver(startK, endK, startD, endD)
      if crossOver != 0:
        if abs(angle) > signal_angle:
          signal_row = row
          if angle > 0:
            openPosition = Position(row['Close'], 'BUY')
          else:
            openPosition = Position(row['Close'], 'SELL')
    else:
      #evaluate
      openedPricePoint = Point(signal_row, row['Close'])
      angle = AngleBtw2Points(startK, endK, startD, endD)
      if abs(angle) > signal_angle_retire:
        openPosition.close(row['Close'])
        positions.append(openPosition)
        openPosition = None 
        signal_row = None 
        openPosition = None 
