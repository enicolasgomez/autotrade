import pandas as pd
import numpy as np
import os.path
#TODO check for compat

from binance.client import Client
import matplotlib.dates as mpl_dates
from Simulator import Simulator
from binance.websockets import BinanceSocketManager
from Ticker import Ticker
from TradeBot import TradeBot
from Historic_Crypto import HistoricalData
live = False

stock = 'BTC-USD'
size = '15m'
api_key = ""
api_secret = ""

ticker = Ticker(stock, size)
trade_bot = TradeBot()

def retrieve_data(symbol, size, start, end):

    file_hash = ''.join([symbol, str(size), start, end, '.pkl'])

    if os.path.isfile(file_hash):
      df = pd.read_pickle(file_hash)
    else:
      df = HistoricalData(symbol, size, start, end).retrieve_data()
      df.to_pickle(file_hash)
    
    df['time'] = pd.to_datetime(df.index)
    df['time'] = df['time'].apply(mpl_dates.date2num)

    df = df.loc[:,['time', 'open', 'high', 'low', 'close']]
    
    return df

if live :
  client = Client(api_key, api_secret)
  bm = BinanceSocketManager(client) 
  bnb_balance = client.get_asset_balance(asset='BTC')
  print("Balance: {}".format(bnb_balance))

  def process_message(msg):
    print("Bid - Ask BTCUSDT price: {} - {}".format(msg['b'], msg['a']))
    ticker.add_tick(msg)

  bm.start_symbol_ticker_socket(stock, process_message)
  bm.start()

else:
  start = '2022-01-01-00-00'
  end = '2022-07-01-00-00'
  #load tick data 
  df = retrieve_data(stock, 1, start, end)
  for tick in df.iterrows():
    ticker.add_tick(tick)


def _new_candle_candler(candle):
  print(candle)
  trade_bot.process_new_candle(candle)

ticker.attach(_new_candle_candler)
  