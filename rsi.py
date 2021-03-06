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

  column_names = ["Date", "Open", "High", "Low", "Close", "Volume"]
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
      close = row['Close']
      new_row = [date, open, current_high, current_low, close, total_vol]
      result_df = pd.concat([pd.DataFrame([new_row],columns=result_df.columns),result_df],ignore_index=True)
      open = 0
      current_index = 0
      current_low = 1000000000
      current_high = 0
      total_vol = 0
  return result_df

rsi_length = 14
end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=950)
stock = 'BTC-USD'
#df = pdr.get_data_yahoo(stock, start_date, end_date)
ticker = yf.Ticker(stock)
df = ticker.history(interval="1D",start="2020-05-05",end="2022-05-18")

#df = to_hourly_data(df, 4)

df['RSI'] = computeRSI(df['Close'], rsi_length)
df['K'], df['D'] = stochastic(df['RSI'], 3, 3, rsi_length)
df['target'] = df['Close'] - df['Open']
#shift up target for next day
df['target'] = df['target'].shift(-1)

#compute last N angles
class Point:
  x = 0
  y = 0
  def __init__(self, x, y):
    self.x = x 
    self.y = y

def AngleBtw2Points(pointA, pointB):
  changeInX = pointB.x - pointA.x
  changeInY = pointB.y - pointA.y
  return math.degrees(math.atan2(changeInY,changeInX)) 

angle_window = 5

for i in range(1, angle_window):
  df['rsi_window_'+str(i)]  = 0

for n, (index, row) in enumerate(df.iterrows()):
  if n > rsi_length + 20:
    for i in range(1,5):
      prev_row = df.iloc[n-i]
      startK = Point(0, prev_row['K']) #using 0 to 100 as SRSI is an oscillator (0, 100)
      startD = Point(0, prev_row['D'])
      endK = Point(100, row['K'])
      endD = Point(100, row['D']) 
      angle = AngleBtw2Points(startK, endK)
      df.iloc[n, df.columns.get_loc('rsi_window_'+str(i))]  = angle

print(df)

from sklearn.compose import make_column_transformer
from sklearn.preprocessing import MinMaxScaler,OneHotEncoder
from sklearn.model_selection import train_test_split

df.reset_index(drop=True, inplace=True)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

df=df.dropna()

#remove first
df = df.iloc[25: , :]

#remove last row
df = df[:-1]

df = df[ abs(df['target']) > 2500 ]
target = df['target']
del df['target']
del df['Dividends']
del df['Stock Splits']

df[df.columns] = scaler.fit_transform(df[df.columns])

target[target>0] = 1
target[target<0] = 0

#binary class
#target = target > 0 

from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier 
from sklearn import metrics

# encoder = LabelEncoder()
# encoder.fit(target)
# target = encoder.transform(target)


from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(df,target,test_size=0.2,
                                               random_state=42)
                                         
# Create Decision Tree classifer object
clf = DecisionTreeClassifier(max_depth=20)

# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)

# Model Accuracy, how often is the classifier correct?
df
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))