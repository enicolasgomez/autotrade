import pandas as pd

class Ticker:

  def __init__(self, symbol, time_frame, live):
    self.symbol = symbol
    self.time_frame = time_frame
    self.ask_candles = pd.DataFrame()
    self.bid_candles = pd.DataFrame()
    self.raw_data = pd.DataFrame()
    self._observers = []
    self.live = live 

  def _notify(self, modifier = None):
    """Alert the observers"""
    for observer in self._observers:
        if modifier != observer:
            observer.update(self)
 
  def attach(self, observer):
      """If the observer is not in the list,append it into the list"""
      if observer not in self._observers:
          self._observers.append(observer)
 
  def detach(self, observer):
      """Remove the observer from the observer list"""
      try:
          self._observers.remove(observer)
      except ValueError:
          pass

  def add_tick(self, tick_data):
    self.raw_data.append(tick_data)
    self._build_candle_data()

  def _build_candle_data(self):
    should_build = False
    #check raw data vs time frame should trigger build
    if should_build:
      ask_df = self.raw_data.assign(Timestamp = pd.to_datetime(self.raw_data['Timestamp'],unit='s')).set_index('Timestamp')
      ask_df.resample(self.time_frame)['Ask'].ohlc()
      self.ask_candles = ask_df 

      bid_df = self.raw_data.assign(Timestamp = pd.to_datetime(self.raw_data['Timestamp'],unit='s')).set_index('Timestamp')
      bid_df.resample(self.time_frame)['Bid'].ohlc()
      self.bid_candles = bid_df
      self._notify()

  def buy(self):
    print("creating buy order ...")
    if self.live:
      buy_order = self.client.create_test_order(symbol=self.symbol, side='BUY', type='MARKET', quantity=100)
      print(buy_order)

  def sell(self):
    print("creating sell order ...")
    if self.live:
      sell_order = self.client.create_test_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=100)
      print(sell_order)





