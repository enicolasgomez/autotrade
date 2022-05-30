import yfinance as yf
from pandas_datareader import data as pdr
import datetime as dt
import talib as ta 
import numpy as np 

yf.pdr_override()

end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=900)
stock = 'BTC-USD'
df = pdr.get_data_yahoo(stock, start_date, end_date)

df['sma5'] = ta.SMA(df['Close'], 2)
df['sma10'] = ta.SMA(df['Close'], 5)
df['rsi5'] = ta.RSI(df['Close'], 5)

deltas = 5

#init columns
for i in range(1, deltas):
  df['sma5_delta_'+str(i)]  = 0
  df['sma10_delta_'+str(i)] = 0
  df['rsi5_delta_'+str(i)] = 0

total = len(df)

for n in range(1, total):
  if n > deltas:
    for i in range(1, deltas):
      df.iloc[n, df.columns.get_loc('sma5_delta_'+str(i))]  = df.iloc[n]['sma5']  - df.iloc[n-i]['sma5']
      df.iloc[n, df.columns.get_loc('sma10_delta_'+str(i))] = df.iloc[n]['sma10'] - df.iloc[n-i]['sma10']
      df.iloc[n, df.columns.get_loc('rsi5_delta_'+str(i))] = df.iloc[n]['sma10'] - df.iloc[n-i]['rsi5']

from sklearn.compose import make_column_transformer
from sklearn.preprocessing import MinMaxScaler,OneHotEncoder
from sklearn.model_selection import train_test_split

df.reset_index(drop=True, inplace=True)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

df=df.dropna()

#shift target 1 up
df['target'] = df['Close'].shift(-1) - df['Close']

#remove first 20 (sma20)
df = df.iloc[25: , :]

#remove last row
df = df[:-1]

target = df['target']
del df['target']

df[df.columns] = scaler.fit_transform(df[df.columns])

target[target>0] = 1
target[target<0] = 0


#binary class
#target = target > 0 

from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

encoder = LabelEncoder()
encoder.fit(target)
target = encoder.transform(target)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(df,target,test_size=0.2,
                                               random_state=42)
                                         

def create_baseline():
	# create model
  model = Sequential()
  model.add(Dense(21, input_dim=21, activation='relu'))
  model.add(Dense(10, input_dim=10, activation='relu'))
  model.add(Dense(2, input_dim=2, activation='relu'))
  model.add(Dense(1, activation='sigmoid'))
	# Compile model
  model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
  return model

# evaluate model with standardized dataset
estimator = KerasClassifier(build_fn=create_baseline, epochs=100, batch_size=5, verbose=0)
kfold = StratifiedKFold(n_splits=10, shuffle=True)
results = cross_val_score(estimator, X_train, y_train, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

#fit the model
#model.fit(X_train,y_train,batch_size=32, epochs=10)

# predicted = model.predict(X_test)
# import matplotlib.pyplot as plt 

# x = range(0, len(y_test))

# plt.plot(x, y_test.values)
# plt.plot(x, predicted)
# plt.title("Results",fontsize=15)
# plt.xlabel("predicted",fontsize=13)
# plt.ylabel("test",fontsize=13)
# plt.grid()
# plt.show()

# print("Completed...")