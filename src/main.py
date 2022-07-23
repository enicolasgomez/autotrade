import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os.path
import operator
#TODO check for compat

from binance.client import Client
import matplotlib.dates as mpl_dates
from binance.streams import BinanceSocketManager
from AutoTrader.Ticker import Ticker
from AutoTrader.TradeBot import TradeBot

from os.path import join, dirname
from dotenv import load_dotenv
from itertools import accumulate
from AutoTrader.PositionType import PositionType

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

live = False
symbol = 'BTCUSDT'
size = 15
api_key = os.environ.get("BINANCE_API_KEY")
api_secret = os.environ.get("BINANCE_API_SECRET")

ticker    = Ticker(size)
trade_bot = TradeBot()
client    = Client(api_key, api_secret)

def plot_profit(p):
  x_axis = range(0, len(p))

  label = 'Profit - Max: {}'.format(str(p[-1]))
  plt.plot(x_axis, p, 'k', label=label )
  plt.legend()
  plt.show()

def _new_candle_observer(candle):
  print(candle.literal())
  trade_bot.process_new_candle(candle.date, candle.open, candle.close, candle.high, candle.low)

def _live_position_observer(params):
  print(params)
  if live:
    type = params[0]
    if type == "OPEN":
      (position_type, take_profit, stop_loss, was_reversal) = params[1]
      order = client.create_test_order(
        symbol=symbol,
        side=Client.SIDE_BUY if position_type == PositionType.BUY else Client.SIDE_SELL ,
        type=Client.ORDER_TYPE_MARKET,
        quantity=100)
      print(order)

ticker.attach(_new_candle_observer)
trade_bot.attach(_live_position_observer)

def retrieve_data(symbol, start, end):

    file_hash = ''.join(['./data/', symbol, start, end, '.pkl'])

    if os.path.isfile(file_hash):
      df = pd.read_pickle(file_hash)
    else:
      klines = np.array(client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, start, end))
      df     = pd.DataFrame(klines.reshape(-1,12),dtype=float, columns = ('Open Time',
                                                                          'Open',
                                                                          'High',
                                                                          'Low',
                                                                          'Close',
                                                                          'Volume',
                                                                          'Close time',
                                                                          'Quote asset volume',
                                                                          'Number of trades',
                                                                          'Taker buy base asset volume',
                                                                          'Taker buy quote asset volume',
                                                                          'Ignore'))
      df.to_pickle(file_hash)

    return df

if live :
  bm = BinanceSocketManager(client) 
  bnb_balance = client.get_asset_balance(asset='BTC')
  print("Balance: {}".format(bnb_balance))

  def process_message(msg):
    print("Bid - Ask BTCUSDT price: {} - {}".format(msg['b'], msg['a']))
    #TODO msg(s) to 1m tick
    ticker.add_tick(msg)

  bm.start_symbol_ticker_socket(symbol, process_message)
  bm.start()

else:
  start = '15 Jun, 2022'
  end   = '15 Jul, 2022'
  df    = retrieve_data(symbol, start, end)

  for index, tick in df.iterrows():
    ticker.add_tick(tick)

  #get graphs
  profit_vector_full              = list(accumulate([1 + p.profitAsPerc for p in trade_bot.closed_positions          ], operator.mul))
  plot_profit(profit_vector_full)
  print("completed")
  